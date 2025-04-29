from libcosimpy.CosimExecution import CosimExecution
from libcosimpy.CosimManipulator import CosimManipulator
from libcosimpy.CosimObserver import CosimObserver
from libcosimpy.CosimSlave import CosimLocalSlave
from libcosimpy.CosimEnums import CosimVariableType
from platform import platform


def test_from_override_set(test_dir):
    execution = CosimExecution.from_step_size(0.1 * 1.0e9)
    local_slave = CosimLocalSlave(
        fmu_path=f"{test_dir}/data/fmi1/identity.fmu", instance_name="Identity"
    )
    execution.add_local_slave(local_slave=local_slave)
    manipulator = CosimManipulator.create_override()
    assert execution.add_manipulator(manipulator=manipulator)
    observer = CosimObserver.create_last_value()
    execution.add_observer(observer=observer)
    slave_index = 0
    variable_references = [0]
    real_values = [1.1]
    integer_values = [11]
    boolean_values = [True]
    string_values = ["Hello World!"]
    assert manipulator.slave_real_values(
        slave_index=slave_index,
        variable_references=variable_references,
        values=real_values,
    )
    assert manipulator.slave_integer_values(
        slave_index=slave_index,
        variable_references=variable_references,
        values=integer_values,
    )
    assert manipulator.slave_boolean_values(
        slave_index=slave_index,
        variable_references=variable_references,
        values=boolean_values,
    )
    assert manipulator.slave_string_values(
        slave_index=slave_index,
        variable_references=variable_references,
        values=string_values,
    )
    execution.step()
    assert (
        observer.last_real_values(
            slave_index=slave_index, variable_references=variable_references
        )
        == real_values
    )
    assert (
        observer.last_integer_values(
            slave_index=slave_index, variable_references=variable_references
        )
        == integer_values
    )
    assert (
        observer.last_boolean_values(
            slave_index=slave_index, variable_references=variable_references
        )
        == boolean_values
    )
    assert observer.last_string_values(
        slave_index=slave_index, variable_references=variable_references
    ) == [sv.encode() for sv in string_values]

    assert manipulator.reset_variables(
        slave_index=slave_index,
        variable_type=CosimVariableType.REAL,
        variable_references=variable_references,
    )
    assert manipulator.reset_variables(
        slave_index=slave_index,
        variable_type=CosimVariableType.INTEGER,
        variable_references=variable_references,
    )
    assert manipulator.reset_variables(
        slave_index=slave_index,
        variable_type=CosimVariableType.BOOLEAN,
        variable_references=variable_references,
    )
    assert manipulator.reset_variables(
        slave_index=slave_index,
        variable_type=CosimVariableType.STRING,
        variable_references=variable_references,
    )
    execution.step()
    assert observer.last_real_values(
        slave_index=slave_index, variable_references=variable_references
    ) == [0.0]
    assert observer.last_integer_values(
        slave_index=slave_index, variable_references=variable_references
    ) == [0]
    assert observer.last_boolean_values(
        slave_index=slave_index, variable_references=variable_references
    ) == [False]
    assert observer.last_string_values(
        slave_index=slave_index, variable_references=variable_references
    ) == ["".encode()]


def test_from_override_set_multiple(test_dir):
    if platform() == "Windows":
        execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/dp-ship")
        manipulator = CosimManipulator.create_override()
        assert execution.add_manipulator(manipulator=manipulator)
        observer = CosimObserver.create_last_value()
        execution.add_observer(observer=observer)
        slave_index = 4
        real_variable_references = [30, 31, 32]
        real_values = [1.1, 2.2, 3.3]
        assert manipulator.slave_real_values(
            slave_index=slave_index,
            variable_references=real_variable_references,
            values=real_values,
        )
        execution.step()
        assert (
            observer.last_real_values(
                slave_index=slave_index, variable_references=real_variable_references
            )
            == real_values
        )
        assert manipulator.reset_variables(
            slave_index=slave_index,
            variable_type=CosimVariableType.REAL,
            variable_references=real_variable_references,
        )
        execution.step()
        assert observer.last_real_values(
            slave_index=slave_index, variable_references=real_variable_references
        ) == [0.0, 0.0, 0.0]


def test_load_scenario(test_dir):
    if platform() == "Windows":
        execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/dp-ship")
        manipulator = CosimManipulator.create_scenario_manager()
        execution.add_manipulator(manipulator=manipulator)
        assert execution.load_scenario(
            manipulator=manipulator,
            scenario_file=f"{test_dir}/data/dp-ship/scenarios/movenorth.json",
        )
        observer = CosimObserver.create_last_value()
        execution.add_observer(observer=observer)
        assert execution.simulate_until(target_time=2.5e9)
        values = observer.last_real_values(slave_index=4, variable_references=[30, 31])
        assert values[0] == 20.0
        assert values[1] == 10.0
        execution.stop()
        assert execution.simulate_until(target_time=3.1e9)
        values = observer.last_real_values(slave_index=4, variable_references=[30, 31])
        assert values[0] == 20.0
        assert values[1] == 25.0
        execution.stop()
        manipulator.abort_scenario()
        assert execution.simulate_until(target_time=3.6e9)
        values = observer.last_real_values(slave_index=4, variable_references=[30, 31])
        assert values[0] == 0.0
        assert values[1] == 0.0
