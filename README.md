# libcosimpy 

Python wrapper for the [libcosim](https://github.com/open-simulation-platform/libcosim/tree/master/src/cosim) library. The wrapper uses the [libcosimc](https://github.com/open-simulation-platform/libcosimc) C wrapper and the python [ctypes](https://docs.python.org/3/library/ctypes.html) library to make OSP accessible to python developers. 

# Getting Started

`libcosimpy` is available from PyPI. Run the following command to install the package:
```bash
pip install libcosimpy
```
To install from the source, run the following command at the root directory of the repository:
```bash
pip install .
```
`libcosimpy` requires [ctypes](https://docs.python.org/3/library/ctypes.html) to call `libcosimc` functions. `ctypes` is included with python and does not have to be installed.

## Tests

Tests can be run using the `pytest` command in the terminal. `libcosimc` log level for all tests can be set in the `./tests/conftest.py` file.