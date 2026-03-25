from __future__ import annotations
import hashlib, os, time
from dataclasses import dataclass, field
from typing import Tuple
from gce.formal_system import ArithmeticFormula, FormalSystem
from gce.godel_numbering import GodelNumbering
from gce.kem_backends import BitCommitmentBody, KemBackend, KemPrivateKey, KemPublicKey

@dataclass(frozen=True)
class GCEPublicKey:
    kem_pk: KemPublicKey
    formal_system_id: str
    security_level: int
    created_timestamp: float = field(default_factory=time.time)

@dataclass(frozen=True)
class GCEPrivateKey:
    kem_sk: KemPrivateKey
    security_level: int

@dataclass(frozen=True)
class GCECommitment:
    body: BitCommitmentBody
    c_g: bytes
    scheme_version: str = 'GCE-MLKEM768-v4'
    def to_bytes(self) -> bytes: return self.body.to_bytes() + self.c_g
    def size_bytes(self) -> int: return len(self.to_bytes())

@dataclass(frozen=True)
class GCEOpening:
    message_bit: int
    randomness: bytes
    formula: ArithmeticFormula

class GodelCryptoEngine:
    def __init__(self, security_level: int=768, formal_system: str='ZFC+Con(ZFC)', backend_name: str='auto') -> None:
        self.kem=KemBackend(backend_name=backend_name, security_level=security_level)
        self.T=FormalSystem(formal_system); self.gnum=GodelNumbering(self.T)
    def keygen(self) -> Tuple[GCEPublicKey, GCEPrivateKey]:
        pk, sk = self.kem.keygen(); return GCEPublicKey(pk, self.T.system_id, 768), GCEPrivateKey(sk, 768)
    def commit(self, public_key: GCEPublicKey, message_bit: int):
        randomness=os.urandom(32); body=self.kem.encapsulate_bit(public_key.kem_pk, message_bit, randomness)
        formula=self.T.encode_commitment_statement(commitment_bytes=body.to_bytes(), message_bit=message_bit, randomness=randomness)
        g_bytes=self.gnum.number_to_bytes(formula); c_g=hashlib.sha3_256(g_bytes + body.to_bytes() + randomness).digest()
        return GCECommitment(body, c_g), GCEOpening(message_bit, randomness, formula)
    def verify(self, public_key: GCEPublicKey, commitment: GCECommitment, opening: GCEOpening) -> bool:
        formula_check=self.T.encode_commitment_statement(commitment_bytes=commitment.body.to_bytes(), message_bit=opening.message_bit, randomness=opening.randomness)
        if formula_check != opening.formula: return False
        g_bytes=self.gnum.number_to_bytes(formula_check); c_g_check=hashlib.sha3_256(g_bytes + commitment.body.to_bytes() + opening.randomness).digest()
        return c_g_check == commitment.c_g
    def open(self, private_key: GCEPrivateKey, commitment: GCECommitment) -> int:
        return self.kem.decapsulate_bit(private_key.kem_sk, commitment.body)
    def backend_report(self): return self.kem.report()
