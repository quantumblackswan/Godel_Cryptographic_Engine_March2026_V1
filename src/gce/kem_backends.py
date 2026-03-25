from __future__ import annotations
import hashlib, hmac, os
from dataclasses import dataclass
from typing import Tuple

class BackendUnavailable(RuntimeError):
    pass

@dataclass(frozen=True)
class KemPublicKey:
    data: bytes
    security_level: int = 768
    def to_bytes(self) -> bytes: return self.data

@dataclass(frozen=True)
class KemPrivateKey:
    data: bytes
    security_level: int = 768
    def to_bytes(self) -> bytes: return self.data

@dataclass(frozen=True)
class KemCiphertext:
    data: bytes
    security_level: int = 768
    def to_bytes(self) -> bytes: return self.data

@dataclass(frozen=True)
class BitCommitmentBody:
    kem_ciphertext: KemCiphertext
    masked_bit: int
    nonce: bytes
    def to_bytes(self) -> bytes:
        return self.kem_ciphertext.to_bytes() + self.nonce + bytes([self.masked_bit])

class BaseKemBackend:
    name='base'; status='experimental'; pk_bytes=1184; sk_bytes=2400; ct_bytes=1088; ss_bytes=32
    @staticmethod
    def _derive_nonce(randomness: bytes, kem_ct: bytes) -> bytes:
        return hashlib.sha3_256(randomness + kem_ct + b'GCE-NONCE').digest()[:32]
    @staticmethod
    def _mask_bit(shared_secret: bytes, nonce: bytes) -> int:
        return hashlib.sha3_256(shared_secret + nonce + b'GCE-BIT-MASK-v1').digest()[0] & 1
    @staticmethod
    def constant_time_equal(a: bytes, b: bytes) -> bool:
        return hmac.compare_digest(a,b)
    def keygen_raw(self) -> Tuple[bytes, bytes]: raise NotImplementedError
    def encaps_raw(self, public_key: bytes) -> Tuple[bytes, bytes]: raise NotImplementedError
    def decaps_raw(self, private_key: bytes, ciphertext: bytes) -> bytes: raise NotImplementedError
    def keygen(self):
        pk, sk = self.keygen_raw(); return KemPublicKey(pk), KemPrivateKey(sk)
    def encapsulate_bit(self, public_key: KemPublicKey, message_bit: int, randomness: bytes) -> BitCommitmentBody:
        ss, kem_ct = self.encaps_raw(public_key.to_bytes())
        nonce = self._derive_nonce(randomness, kem_ct)
        masked_bit = message_bit ^ self._mask_bit(ss, nonce)
        return BitCommitmentBody(KemCiphertext(kem_ct), masked_bit, nonce)
    def decapsulate_bit(self, private_key: KemPrivateKey, body: BitCommitmentBody) -> int:
        ss = self.decaps_raw(private_key.to_bytes(), body.kem_ciphertext.to_bytes())
        return body.masked_bit ^ self._mask_bit(ss, body.nonce)

class KeeperMlkemBackend(BaseKemBackend):
    name='keeper_mlkem_native'; status='research-friendly, stronger third-party backend'
    def __init__(self):
        from mlkem import ML_KEM, MLKEM_768_PARAMETERS
        self._backend = ML_KEM(MLKEM_768_PARAMETERS)
    def keygen_raw(self): return self._backend.key_gen()
    def encaps_raw(self, public_key: bytes):
        ss, ct = self._backend.encaps(public_key); return ss, ct
    def decaps_raw(self, private_key: bytes, ciphertext: bytes):
        return self._backend.decaps(private_key, ciphertext)

class LegacyMlkemAlphaBackend(BaseKemBackend):
    name='legacy_mlkem_alpha'; status='experimental'
    def __init__(self):
        from mlkem.ml_kem import ML_KEM
        from mlkem.parameter_set import ML_KEM_768
        self._backend = ML_KEM(ML_KEM_768, fast=True)
    def keygen_raw(self): return self._backend.key_gen()
    def encaps_raw(self, public_key: bytes):
        ss, ct = self._backend.encaps(public_key); return ss, ct
    def decaps_raw(self, private_key: bytes, ciphertext: bytes):
        return self._backend.decaps(private_key, ciphertext)

class LibFips203Backend(BaseKemBackend):
    name='libfips203_wrapper'; status='optional; requires working libfips203 installation'
    def __init__(self):
        try:
            import fips203
        except Exception as e:
            raise BackendUnavailable(f'fips203 import failed: {e}')
        self._module = fips203
        self._backend = fips203.ML_KEM_768
    def keygen_raw(self):
        ek, dk = self._backend.keygen(); return bytes(ek), bytes(dk)
    def encaps_raw(self, public_key: bytes):
        ek = self._module.EncapsulationKey(public_key)
        ct, ss = ek.encaps(); return ss, bytes(ct)
    def decaps_raw(self, private_key: bytes, ciphertext: bytes):
        dk = self._module.DecapsulationKey(private_key)
        ct = self._module.CipherText(ciphertext)
        return dk.decaps(ct)

class SimulatedKemBackend(BaseKemBackend):
    name='simulated_api_only'; status='not cryptographically secure'
    @staticmethod
    def _expand(seed: bytes, out_len: int) -> bytes: return hashlib.shake_256(seed).digest(out_len)
    def keygen_raw(self):
        pk=self._expand(os.urandom(32), self.pk_bytes); sk=self._expand(os.urandom(32), self.sk_bytes-self.pk_bytes)+pk; return pk, sk
    def encaps_raw(self, public_key: bytes):
        ss=hashlib.sha3_256(public_key+b'SIM-SS').digest(); ct=self._expand(hashlib.sha3_256(public_key+b'SIM-CT').digest(), self.ct_bytes); return ss, ct
    def decaps_raw(self, private_key: bytes, ciphertext: bytes):
        public_key=private_key[-self.pk_bytes:]; return hashlib.sha3_256(public_key+b'SIM-SS').digest()

BACKEND_REGISTRY={'keeper_mlkem_native': KeeperMlkemBackend, 'legacy_mlkem_alpha': LegacyMlkemAlphaBackend, 'libfips203_wrapper': LibFips203Backend, 'simulated_api_only': SimulatedKemBackend}

class KemBackend:
    def __init__(self, backend_name: str='auto', security_level: int=768):
        self.security_level = security_level
        self._backend = self._select(backend_name)
        self.name=self._backend.name; self.status=self._backend.status; self.pk_bytes=self._backend.pk_bytes; self.sk_bytes=self._backend.sk_bytes; self.ct_bytes=self._backend.ct_bytes; self.ss_bytes=self._backend.ss_bytes
    def _select(self, backend_name: str):
        if backend_name!='auto': return BACKEND_REGISTRY[backend_name]()
        for cls in (KeeperMlkemBackend, LegacyMlkemAlphaBackend, LibFips203Backend):
            try: return cls()
            except Exception: pass
        return SimulatedKemBackend()
    def keygen(self): return self._backend.keygen()
    def encapsulate_bit(self, public_key, message_bit, randomness): return self._backend.encapsulate_bit(public_key, message_bit, randomness)
    def decapsulate_bit(self, private_key, body): return self._backend.decapsulate_bit(private_key, body)
    def report(self):
        return {'backend': self.name, 'status': self.status, 'security_level': self.security_level, 'public_key_bytes': self.pk_bytes, 'private_key_bytes': self.sk_bytes, 'kem_ciphertext_bytes': self.ct_bytes, 'commitment_body_bytes': self.ct_bytes+32+1, 'godel_hash_bytes': 32, 'approx_total_commitment_bytes': self.ct_bytes+32+1+32}
