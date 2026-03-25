
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

class KeeperWrapperUnavailable(RuntimeError):
    pass

@dataclass(frozen=True)
class KeeperPublicKey:
    data: bytes
    def to_bytes(self) -> bytes: return self.data

@dataclass(frozen=True)
class KeeperPrivateKey:
    data: bytes
    def to_bytes(self) -> bytes: return self.data

@dataclass(frozen=True)
class KeeperCiphertext:
    data: bytes
    def to_bytes(self) -> bytes: return self.data

class KeeperMlkemSkeleton:
    """Skeleton adapter for a Keeper-style ML-KEM package."""
    backend_name='keeper_mlkem_skeleton'
    def __init__(self) -> None:
        try:
            from mlkem import ML_KEM, MLKEM_768_PARAMETERS
        except Exception as exc:
            raise KeeperWrapperUnavailable(str(exc)) from exc
        self._backend = ML_KEM(MLKEM_768_PARAMETERS)
    def keygen(self) -> Tuple[KeeperPublicKey, KeeperPrivateKey]:
        pk, sk = self._backend.key_gen(); return KeeperPublicKey(pk), KeeperPrivateKey(sk)
    def encaps(self, public_key: KeeperPublicKey) -> Tuple[bytes, KeeperCiphertext]:
        ss, ct = self._backend.encaps(public_key.to_bytes()); return ss, KeeperCiphertext(ct)
    def decaps(self, private_key: KeeperPrivateKey, ciphertext: KeeperCiphertext) -> bytes:
        return self._backend.decaps(private_key.to_bytes(), ciphertext.to_bytes())
