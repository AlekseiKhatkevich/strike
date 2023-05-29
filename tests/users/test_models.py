import pytest
import os

def test_mani():
    assert 1+1 == 2
    assert os.environ['SECRET_STRING'] == 'rr'
    assert os.environ['test'] == '228'