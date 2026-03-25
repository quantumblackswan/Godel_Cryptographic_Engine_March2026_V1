
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

class LibFips203WrapperUnavailable(RuntimeError):
    pass

@dataclass(frozen=True)
class Fips203PublicKey:
    data: bytes
    def to_bytes(self) -> bytes: return self.data

@dataclass(frozen=True)
class Fips203PrivateKey:
    data: bytes
    def to_bytes(self) -> bytes: return self.data

@dataclass(frozen=True)
class Fips203Ciphertext:
    data: bytes
    def to_bytes(self) -> bytes: return self.data

class LibFips203Skeleton:
    """Skeleton adapter for Python fips203/libfips203 bindings."""
    backend_name='libfips203_skeleton'
    def __init__(self) -> None:
        try:
            import fips203
        except Exception as exc:
            raise LibFips203WrapperUnavailable(str(exc)) from exc
        try:
            self._module = fips203
            self._backend = fips203.ML_KEM_768
        except Exception as exc:
            raise LibFips203WrapperUnavailable(str(exc)) from exc
    def keygen(self) -> Tuple[Fips203PublicKey, Fips203PrivateKey]:
        ek, dk = self._backend.keygen(); return Fips203PublicKey(bytes(ek)), Fips203PrivateKey(bytes(dk))
    def encaps(self, public_key: Fips203PublicKey) -> Tuple[bytes, Fips203Ciphertext]:
        ek = self._module.EncapsulationKey(public_key.to_bytes())
        ct, ss = ek.encaps(); return ss, Fips203Ciphertext(bytes(ct))
    def decaps(self, private_key: Fips203PrivateKey, ciphertext: Fips203Ciphertext) -> bytes:
        dk = self._module.DecapsulationKey(private_key.to_bytes())
        ct = self._module.CipherText(ciphertext.to_bytes())
        return dk.decaps(ct)
