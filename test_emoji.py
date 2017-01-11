# content of test_sysexit.py
import pytest
from buildDataFiles import DataFilerBuilder
from workflow import Workflow3
def f():
    raise SystemExit(1)

def test_mytest():
    with pytest.raises(SystemExit):
        f()

def test_data_builder():
    DataFilerBuilder().buildData(Workflow3())
