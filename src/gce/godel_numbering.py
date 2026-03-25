from __future__ import annotations
import hashlib
from gce.formal_system import ArithmeticFormula
class GodelNumbering:
    def __init__(self, formal_system) -> None:
        self.formal_system = formal_system
    def number_to_bytes(self, formula: ArithmeticFormula) -> bytes:
        return hashlib.sha3_256(formula.canonical()).digest()
