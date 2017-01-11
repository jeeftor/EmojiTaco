# content of test_sysexit.py
import pytest
from buildDataFiles import DataFilerBuilder
from workflow import Workflow3
from bs4 import BeautifulSoup
import sys
import lxml


def f():
    raise SystemExit(1)

def test_mytest():
    soup = BeautifulSoup("<html>data</html>")
    soup = BeautifulSoup("<html></html>", "lxml")

    with pytest.raises(SystemExit):
        f()

def test_data_builder():
    DataFilerBuilder().buildData(Workflow3(), test_mode=True)
