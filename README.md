# libcosimpy 

Python wrapper for the [libcosim](https://github.com/open-simulation-platform/libcosim/tree/master/src/cosim) library. The wrapper uses the [libcosimc](https://github.com/open-simulation-platform/libcosimc) C wrapper and the [ctypes](https://docs.python.org/3/library/ctypes.html) library to make OSP accessible to Python developers.   

# Getting Started

`libcosimpy` is available from PyPI. Run the following command to install the package:
```bash
pip install libcosimpy
```
To install from the source, run the following command at the root directory of the repository:
```bash
pip install .
```
`libcosimpy` requires [ctypes](https://docs.python.org/3/library/ctypes.html) to call `libcosimc` functions. `ctypes` is included with Python and does not have to be installed.

# Usage

## Create execution

Import `CosimExecution` from `libcosimpy`

```python
from libcosimpy.CosimExecution import CosimExecution
```

#### Empty execution object

```python
execution = CosimExecution.from_step_size(step_size=1e3)
```

With a 0.01s fixed time step

#### From OSP config

```python
execution = CosimExecution.from_osp_config_file(osp_path=f'[PATH_TO_OSP_DIRECTORY]')
```

#### From SSP config

```python
execution = CosimExecution.from_ssp_file(ssp_path=f'[PATH_TO_SSP_DIRECTORY]')
```

## Add slave

FMUs can be added manually to execution. OSP and SSP config executions will import all required slaves automatically and this step is not required  

Import `CosimLocalSlave` from `libcosimpy`

```python
from libcosimpy.CosimSlave import CosimLocalSlave
```

Add slave to existing execution 

```python
local_slave = CosimLocalSlave(fmu_path=f'[PATH_WITH_FILENAME_TO_FMU]', instance_name='[SOME_UNIQUE_NAME]')
slave_index = execution.add_local_slave(local_slave=local_slave)
```

Slave index is used for future referencing to the model

## Run simulation

Simulations can either be run continiously for a duration

```python
execution.simulate_until(target_time=10e9)
```

To simulate for 10s

Or stepped manually

```python
execution.step()
```

With option for stepping multiple steps at once

```python
execution.step(step_count=10)
```

## Finding slave and variable indices

List of slave indices and corresponding indices can be fetched from execution

```python
slave_infos = list(execution.slave_infos())
```

List of model variables and corresponding indices can be fetched

```python
variables = execution.slave_variables(slave_index=slave_index)
```

The indices can also be found by unzipping the FMU-file and inspecting the `modelDescription.xml` file 

## Retrieving values from simulation

Import `CosimObserver` from `libcosimpy`

```python
from libcosimpy.CosimObserver import CosimObserver
```

Observers can be used to retrieve values as Python list

```python
observer = CosimObserver.create_last_value()
execution.add_observer(observer=observer)

# Run simulation
...
# Retrieve floating point values
values = observer.last_real_values(slave_index=[SLAVE_INDEX], # Model to monitor (integer)
                                   variable_references=[VALUE_REFERENCE(s)]) # List of indices to monitor (integer)
```

Time series and file export observers are also supported 

## Overriding values in simulation

Import `CosimManipulator` from `libcosimpy`

```python
from libcosimpy.CosimManipulator import CosimManipulator
```

Manipulators are used to override values

```python
manipulator = CosimManipulator.create_override()
execution.add_manipulator(manipulator=manipulator)

# Run simulation
...
# Override floating point values
manipulator.slave_real_values(slave_index=[SLAVE_INDEX], # Model to monitor (integer) 
                              variable_references=[VALUE_REFERENCE(s)], # Index or list of indices to manipulate (integer)
                              values=[SOME_OVERRIDE_VALUE(s)]) # Floating point values used for override. Equal length to variable references
execution.step()
```

Scenario manipulators are also supported

# Tests

Tests can be run using the `pytest` command in the terminal. `libcosimc` log level for all tests can be set in the `./tests/conftest.py` file.
