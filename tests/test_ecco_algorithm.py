from libcosimpy.CosimAlgorithm import CosimAlgorithm, EccoParams
from libcosimpy.CosimExecution import CosimExecution
from libcosimpy.CosimObserver import CosimObserver
from libcosimpy.CosimSlave import CosimLocalSlave
from libcosimpy._internal import get_last_error_message


def test_ecco_algorithm_create():
    params = EccoParams()
    ecco_algorithm = CosimAlgorithm.create_ecco_algorithm(params)
    assert ecco_algorithm is not None


def test_ecco_algorithm_simulate(test_dir: str):
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
    ecco_algorithm = CosimAlgorithm.create_ecco_algorithm(params)
    assert ecco_algorithm

    # Create execution
    execution = CosimExecution.from_algorithm(ecco_algorithm)
    assert execution

    # Adding models and observers
    chassis = CosimLocalSlave(fmu_path=f"{test_dir}/data/fmi2/quarter_truck/Chassis.fmu", instance_name="chassiss")
    chassis_index = execution.add_local_slave(chassis)
    wheel = CosimLocalSlave(fmu_path=f"{test_dir}/data/fmi2/quarter_truck/Wheel.fmu", instance_name="wheels")
    wheel_index = execution.add_local_slave(wheel)

    assert chassis_index == 0
    assert wheel_index == 1

    observer = CosimObserver.create_time_series(buffer_size=50000)
    assert execution.add_observer(observer)

    assert execution.real_time_simulation_enabled(False)

    execution.simulate_until(4 * 1e9)

