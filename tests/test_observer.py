from libcosimpy.CosimExecution import CosimExecution
from libcosimpy.CosimObserver import CosimObserver
from libcosimpy.CosimSlave import CosimLocalSlave
from libcosimpy.CosimEnums import CosimVariableType
from os import listdir
from platform import platform


def test_from_last_value_observer_read(test_dir):
    if platform() == "Windows":
        execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/dp-ship")
        observer = CosimObserver.create_last_value()
        assert execution.add_observer(observer=observer)
        execution.step()
        slave_index = 4
        real_variables_list = [3, 4, 6]
        real_value_list = observer.last_real_values(
            slave_index=slave_index, variable_references=real_variables_list
        )
        assert len(real_value_list) == len(real_variables_list)
        for idx, value in enumerate(real_value_list):
            if idx == 0:
                assert value == 0.003
            elif idx == 1:
                assert value == 0.1
            else:
                assert value == 0.0001
        integer_variables_list = [0]
        integer_value_list = observer.last_integer_values(
            slave_index=slave_index, variable_references=integer_variables_list
        )
        assert integer_value_list[0] == 1000
        boolean_variables_list = [0]
        boolean_value_list = observer.last_boolean_values(
            slave_index=slave_index, variable_references=boolean_variables_list
        )
        assert boolean_value_list[0]
        string_variables_list = [0]
        string_value_list = observer.last_string_values(
            slave_index=slave_index, variable_references=string_variables_list
        )
        assert string_value_list[0] == "Euler".encode()


def test_from_dir(test_dir):
    execution = CosimExecution.from_step_size(0.1 * 1.0e9)
    local_slave = CosimLocalSlave(
        fmu_path=f"{test_dir}/data/fmi1/identity.fmu", instance_name="test_from_dir"
    )
    execution.add_local_slave(local_slave=local_slave)
    observer = CosimObserver.create_to_dir(log_dir=r"./tests/log")
    execution.add_observer(observer=observer)
    execution.step()
    log_files = listdir(r"./tests/log")
    log_file_found = False
    for file in log_files:
        if "test_from_dir" in file:
            log_file_found = True
            break
    assert log_file_found


def test_from_time_series(test_dir):
    execution = CosimExecution.from_step_size(0.1 * 1.0e9)
    local_slave = CosimLocalSlave(
        fmu_path=f"{test_dir}/data/fmi1/identity.fmu", instance_name="test_from_dir"
    )
    execution.add_local_slave(local_slave=local_slave)
    value_reference = 0
    from_step = 1
    observer = CosimObserver.create_time_series()
    execution.add_observer(observer=observer)
    assert observer.start_time_series(
        0, value_reference=value_reference, variable_type=CosimVariableType.INTEGER
    )
    assert observer.start_time_series(
        0, value_reference=value_reference, variable_type=CosimVariableType.REAL
    )
    execution.step(step_count=5)
    real_time_points, real_step_numbers, real_samples = (
        observer.time_series_real_samples(
            0, value_reference=value_reference, sample_count=10, from_step=from_step
        )
    )
    assert real_time_points == [100000000, 200000000, 300000000, 400000000, 500000000]
    assert real_step_numbers == [1, 2, 3, 4, 5]
    assert len(real_time_points) == 5
    assert real_step_numbers[0] == 1
    assert real_time_points[0] == 100000000
    assert real_step_numbers[4] == 5
    assert real_time_points[4] == 500000000
    integer_time_points, integer_step_numbers, integer_samples = (
        observer.time_series_integer_samples(
            0, value_reference=value_reference, sample_count=10, from_step=from_step
        )
    )
    assert len(integer_time_points) == 5
    assert integer_step_numbers[0] == 1
    assert integer_time_points[0] == 100000000
    assert integer_step_numbers[4] == 5
    assert integer_time_points[4] == 500000000
    assert observer.stop_time_series(
        slave_index=0,
        value_reference=value_reference,
        variable_type=CosimVariableType.INTEGER,
    )
    assert observer.stop_time_series(
        slave_index=0,
        value_reference=value_reference,
        variable_type=CosimVariableType.REAL,
    )
    observer1 = CosimObserver.create_time_series(buffer_size=3)
    execution.add_observer(observer=observer1)
    assert observer1.start_time_series(
        slave_index=0,
        value_reference=value_reference,
        variable_type=CosimVariableType.INTEGER,
    )
    execution.step(step_count=2)
    from_step1 = 7
    integer_time_points1, integer_step_numbers1, integer_samples1 = (
        observer1.time_series_integer_samples(
            slave_index=0,
            value_reference=value_reference,
            sample_count=10,
            from_step=from_step1,
        )
    )
    assert integer_step_numbers1 == [7]
    assert integer_time_points1 == [700000000]
    observer2 = CosimObserver.create_time_series(buffer_size=3)
    execution.add_observer(observer=observer2)
    assert observer2.start_time_series(
        slave_index=0,
        value_reference=value_reference,
        variable_type=CosimVariableType.INTEGER,
    )
    execution.step(step_count=5)
    from_step2 = 7
    integer_time_points2, integer_step_numbers2, integer_samples2 = (
        observer2.time_series_integer_samples(
            slave_index=0,
            value_reference=value_reference,
            sample_count=10,
            from_step=from_step2,
        )
    )
    assert len(integer_time_points2) == 3
