import copy
from hypothesis import given, settings, strategies as st
from gce.engine import GodelCryptoEngine
@given(st.integers(min_value=0, max_value=1))
@settings(max_examples=15)
def test_round_trip(bit):
    eng=GodelCryptoEngine(backend_name='keeper_mlkem_native'); pk, sk = eng.keygen(); c, o = eng.commit(pk, bit)
    assert eng.verify(pk,c,o) is True
    assert eng.open(sk,c)==bit
@given(st.integers(min_value=0, max_value=1))
@settings(max_examples=10)
def test_wrong_opening(bit):
    eng=GodelCryptoEngine(backend_name='keeper_mlkem_native'); pk, sk = eng.keygen(); c, o = eng.commit(pk, bit)
    bad=copy.deepcopy(o); object.__setattr__(bad,'message_bit',1-bit)
    assert eng.verify(pk,c,bad) is False
def test_size():
    eng=GodelCryptoEngine(backend_name='keeper_mlkem_native'); pk, _ = eng.keygen(); c, _ = eng.commit(pk,1)
    assert c.size_bytes()==1153
