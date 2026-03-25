from __future__ import annotations
import hashlib
from dataclasses import dataclass

@dataclass(frozen=True)
class ArithmeticFormula:
    statement: str
    message_bit: int
    randomness_hex: str
    commitment_fingerprint_hex: str
    formal_system_id: str
    def canonical(self) -> bytes:
        return (f"{self.formal_system_id}|{self.message_bit}|{self.randomness_hex}|{self.commitment_fingerprint_hex}|{self.statement}").encode("utf-8")

class FormalSystem:
    def __init__(self, system_id: str = "ZFC+Con(ZFC)") -> None:
        self.system_id = system_id
    def encode_commitment_statement(self, *, commitment_bytes: bytes, message_bit: int, randomness: bytes) -> ArithmeticFormula:
        fp = hashlib.sha3_256(commitment_bytes).hexdigest()
        stmt = ("Exists a valid ML-KEM-768 transcript and 1-bit DEM mask such that "
                f"the published opening evaluates to {message_bit} under randomness tag {hashlib.sha3_256(randomness).hexdigest()[:16]}.")
        return ArithmeticFormula(stmt, message_bit, randomness.hex(), fp, self.system_id)
