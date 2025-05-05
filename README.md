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

# Using ECCO algorithm

Libcosimpy supports ECCO (Energy-Conservation-based Co-Simulation) algorithm based on the work in [1] for adaptively
updating the step size of the simulation. The algorithm uses the law of conservation of energy between FMU models that
represent power bonds from bond graph theory. 

## Creating ECCO algorithm manually
The parameters of the algorithm can be specified via the `EccoParam` class:

```python
params = EccoParams(
    safety_factor=0.8,
    step_size=1e-4,
    min_step_size=1e-4,
    max_step_size=0.01,
    min_change_rate=0.2,
    max_change_rate=1.5,
    abs_tolerance=1e-4,
    rel_tolerance=1e-4,
    p_gain=0.2,
    i_gain=0.15,
)
```

The algorithm be created via `create_ecco_algorithm`, which can be used to create a new execution instance:

```python
# Create an algorithm instance
ecco_algorithm = CosimAlgorithm.create_ecco_algorithm(params)

# Create execution
execution = CosimExecution.from_algorithm(ecco_algorithm)
```

The power bond between models is represented by input and output connection pair between two models:

```python
# Indicating a power bond between models (indicated by index chassis_index and wheel_index)
ecco_algorithm.add_power_bond(
    chassis_index,
    chassis_v_out,
    chassis_f_in,
    wheel_index,
    wheel_f_out,
    wheel_v_in,
)
```

The simulation is started as usual via `simulate_until` function from `CosimExecution`:
```python
execution.simulate_until(target_time=10e9)
```

See [test_ecco_algorithm](tests/test_ecco_algorithm.py) for detailed usage of ECCO algorithm.

## Creating ECCO algorithm via system structure file

Alternatively, ECCO algorithm can also be created via system structure file:
```xml
<OspSystemStructure xmlns="http://opensimulationplatform.com/MSMI/OSPSystemStructure" version="0.1">
    ...
    <!-- Specify ecco algorithm -->
    <Algorithm>ecco</Algorithm>
    ...
    <Connections>
        <!-- Annotate variable connection as power bond via `powerBond` attribute. Specify
             causality of the variable (input or output) -->
        <VariableConnection powerBond="wheelchassis">
            <Variable simulator="chassis" name="velocity" causality="input"/>
            <Variable simulator="wheel" name="in_vel" causality="output"/>
        </VariableConnection>
        <VariableConnection powerBond="wheelchassis">
            <Variable simulator="wheel" name="out_spring_damper_f" causality="input"/>
            <Variable simulator="chassis" name="force" causality="output"/>
        </VariableConnection>
    </Connections>
    <!-- Specify ecco algorithm parameters -->
    <EccoConfiguration>
        <SafetyFactor>0.99</SafetyFactor>
        <StepSize>0.0001</StepSize>
        <MinimumStepSize>0.00001</MinimumStepSize>
        <MaximumStepSize>0.01</MaximumStepSize>
        <MinimumChangeRate>0.2</MinimumChangeRate>
        <MaximumChangeRate>1.5</MaximumChangeRate>
        <ProportionalGain>0.2</ProportionalGain>
        <IntegralGain>0.15</IntegralGain>
        <RelativeTolerance>1e-6</RelativeTolerance>
        <AbsoluteTolerance>1e-6</AbsoluteTolerance>
    </EccoConfiguration>
</OspSystemStructure>
```

Then this file can be loaded via a usual way via `CosimExecution.from_osp_config_file`:
```python
execution = CosimExecution.from_osp_config_file(osp_path="tests/data/fmi2/quarter_truck")
```

See [Quarter truck example](tests/data/fmi2/quarter_truck/OspSystemStructure.xml) for detailed usage of ECCO algorithm via system structure file.


## Reference
[1] Sadjina, S. and Pedersen, E., 2020. Energy conservation and coupling error reduction in non-iterative co-simulations. Engineering with Computers, 36, pp.1579-1587.


# Tests

Tests can be run using the `pytest` command in the terminal. `libcosimc` log level for all tests can be set in the `./tests/conftest.py` file.
