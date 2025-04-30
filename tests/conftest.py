from libcosimpy.CosimLogging import log_output_level, CosimLogLevel
import shutil
import pytest
from os.path import dirname as d
from os.path import abspath

# Reduce log outputs while running tests
log_output_level(CosimLogLevel.FATAL)

# Clear content of test log folder
try:
    shutil.rmtree(r"./tests/log")
except OSError as e:
    print("Error: %s : %s" % (r"./tests/log", e.strerror))


@pytest.fixture(scope="module")
def test_dir():
    return d(abspath(__file__))
