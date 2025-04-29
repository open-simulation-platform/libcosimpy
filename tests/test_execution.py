import time
from platform import platform

from pytest import raises
from libcosimpy.CosimExecution import CosimExecution
from libcosimpy.CosimEnums import CosimExecutionState
from libcosimpy.CosimObserver import CosimObserver
from libcosimpy.CosimSlave import CosimLocalSlave


def test_invalid_execution_creation():
    with raises(AssertionError) as e_info:
        CosimExecution()
        assert "initialized" in str(e_info.value)


def test_invalid_create_key():
    with raises(AssertionError) as e_info:
        CosimExecution(create_key=object(), execution_ptr=None)
        assert "initialized"


def test_num_slaves_and_variables(test_dir):
    if platform() == "Windows":
        execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
        assert execution.num_slaves() == 2
        assert execution.num_slave_variables(slave_index=0) == 217


def test_num_slaves_zero():
    execution = CosimExecution.from_step_size(step_size=1e3)
    assert execution.num_slaves() == 0


def test_start(test_dir):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    execution_status = execution.status()
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    execution.start()
    time.sleep(0.1)
    execution_status = execution.status()
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.RUNNING


def test_step(test_dir):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    execution_status = execution.status()
    assert execution_status.current_time == 0.0
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    execution.step()
    execution_status = execution.status()
    assert execution_status.current_time == 0.1e6
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED


def test_simulate_until(test_dir):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    execution_status = execution.status()
    assert execution_status.current_time == 0.0
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    execution.simulate_until(target_time=1e9)
    execution_status = execution.status()
    assert execution_status.current_time == 1e9
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED


def test_simulate_until_int(test_dir):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    execution_status = execution.status()
    assert execution_status.current_time == 0.0
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    execution.simulate_until(target_time=1000000000)
    execution_status = execution.status()
    assert execution_status.current_time == 1e9
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED


def test_simulate_until_zero(test_dir):
    with raises(AssertionError) as e_info:
        execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
        execution.simulate_until(target_time=0)
        assert "non-zero" in str(e_info.value)


def test_simulate_until_none(test_dir):
    with raises(TypeError) as e_info:
        execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
        execution.simulate_until(target_time=None)
        assert "convertible" in str(e_info.value)


def test_simulate_until_invalid(test_dir):
    with raises(ValueError) as e_info:
        execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
        execution.simulate_until(target_time="non-valid")
        assert "convertible" in str(e_info.value)


def test_running_state(test_dir):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    execution_status = execution.status()
    assert execution_status.current_time == 0.0
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    execution.start()
    execution_status = execution.status()
    time.sleep(0.1)
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.RUNNING
    execution.stop()
    execution_status = execution.status()
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    assert execution_status.current_time != 0.0


def test_real_time_simulation(test_dir):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    execution_status = execution.status()
    assert not execution_status.is_real_time_simulation
    execution.real_time_simulation_enabled()
    execution_status = execution.status()
    assert execution_status.is_real_time_simulation
    execution.real_time_simulation_enabled(enabled=False)
    execution_status = execution.status()
    assert not execution_status.is_real_time_simulation


def test_real_time_factor_target(test_dir):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    execution_status = execution.status()
    assert execution_status.real_time_factor_target == 1.0
    assert execution.real_time_factor_target(real_time_factor=5.0)
    execution_status = execution.status()
    assert execution_status.real_time_factor_target == 5.0


def test_real_time_factor_target_zero(test_dir):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    assert execution.real_time_factor_target(real_time_factor=0.0)


def test_real_time_factor_target_invalid(test_dir):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    assert execution.real_time_factor_target(real_time_factor=-1.0) == 1


def test_steps_to_monitor(test_dir):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    execution_status = execution.status()
    assert execution_status.steps_to_monitor == 5
    execution.steps_to_monitor(step_count=10)
    execution_status = execution.status()
    assert execution_status.steps_to_monitor == 10


def test_steps_to_monitor_zero(test_dir):
    with raises(AssertionError) as e_info:
        execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
        execution.steps_to_monitor(step_count=0)
        assert "non-zero" in str(e_info.value)


def test_initial_value(test_dir):
    execution = CosimExecution.from_step_size(0.1 * 1.0e9)
    print(f"{test_dir}/data/fmi1/identity.fmu")
    local_slave = CosimLocalSlave(
        fmu_path=f"{test_dir}/data/fmi1/identity.fmu", instance_name="Identity"
    )
    slave_index = execution.add_local_slave(local_slave=local_slave)
    assert slave_index == 0
    variable_reference = 0
    observer = CosimObserver.create_last_value()
    assert execution.add_observer(observer=observer)
    real_value = 1.2
    assert execution.real_initial_value(
        slave_index=slave_index, variable_reference=variable_reference, value=real_value
    )
    integer_value = -5
    assert execution.integer_initial_value(
        slave_index=slave_index,
        variable_reference=variable_reference,
        value=integer_value,
    )
    boolean_value = True
    assert execution.boolean_initial_value(
        slave_index=slave_index,
        variable_reference=variable_reference,
        value=boolean_value,
    )
    string_value = "Hello World!"
    assert execution.string_initial_value(
        slave_index=slave_index,
        variable_reference=variable_reference,
        value=string_value,
    )
    execution.step()
    assert observer.last_real_values(
        slave_index=slave_index, variable_references=[variable_reference]
    ) == [real_value]
    assert observer.last_integer_values(
        slave_index=slave_index, variable_references=[variable_reference]
    ) == [integer_value]
    assert observer.last_boolean_values(
        slave_index=slave_index, variable_references=[variable_reference]
    ) == [boolean_value]
    assert observer.last_string_values(
        slave_index=slave_index, variable_references=[variable_reference]
    ) == [string_value.encode()]


def test_slave_index_from_instance_name(test_dir):
    if platform() == "Windows":
        execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
        slave_index = execution.slave_index_from_instance_name("KnuckleBoomCrane")
        assert slave_index == 0


def test_slave_variables(test_dir):
    execution = CosimExecution.from_step_size(0.1 * 1.0e9)
    local_slave = CosimLocalSlave(
        fmu_path=f"{test_dir}/data/fmi1/identity.fmu", instance_name="Identity"
    )
    slave_index = execution.add_local_slave(local_slave=local_slave)
    variables = execution.slave_variables(slave_index=slave_index)
    assert len(variables) == 8
    for idx, variable in enumerate(variables):
        if idx == 0:
            assert variable.name == "realIn".encode()
        elif idx == 1:
            assert variable.name == "integerIn".encode()
        elif idx == 2:
            assert variable.name == "booleanIn".encode()
            break
