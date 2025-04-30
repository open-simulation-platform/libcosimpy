from libcosimpy.CosimAlgorithm import CosimAlgorithm, EccoParams
from libcosimpy.CosimEnums import CosimVariableType
from libcosimpy.CosimExecution import CosimExecution
from libcosimpy.CosimObserver import CosimObserver
from libcosimpy.CosimSlave import CosimLocalSlave


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
    chassis = CosimLocalSlave(fmu_path=f"{test_dir}/data/fmi2/quarter_truck/Chassis.fmu", instance_name="chassis")
    chassis_index = execution.add_local_slave(chassis)
    wheel = CosimLocalSlave(fmu_path=f"{test_dir}/data/fmi2/quarter_truck/Wheel.fmu", instance_name="wheel")
    wheel_index = execution.add_local_slave(wheel)

    assert chassis_index == 0
    assert wheel_index == 1

    observer = CosimObserver.create_time_series(buffer_size=500000)
    assert execution.add_observer(observer)
    assert execution.real_time_simulation_enabled(False)

    # Connections
    chassis_v_out = 23
    chassis_f_in = 4
    wheel_f_out = 15
    wheel_v_in = 7

    observer.start_time_series(chassis_index, chassis_v_out, CosimVariableType.REAL)
    observer.start_time_series(chassis_index, chassis_f_in, CosimVariableType.REAL)
    observer.start_time_series(wheel_index, wheel_f_out, CosimVariableType.REAL)
    observer.start_time_series(wheel_index, wheel_v_in, CosimVariableType.REAL)

    assert execution.connect_real_variables(chassis_index, chassis_v_out, wheel_index, wheel_v_in) > -1
    assert execution.connect_real_variables(wheel_index, wheel_f_out, chassis_index, chassis_f_in) > -1

    assert (
        ecco_algorithm.add_power_bond(
            chassis_index,
            chassis_v_out,
            chassis_f_in,
            wheel_index,
            wheel_f_out,
            wheel_v_in,
        )
        > -1
    )

    assert execution.real_initial_value(chassis_index, 8, 400)  # mass
    assert execution.string_initial_value(chassis_index, 1, "Euler")  # solver
    assert execution.real_initial_value(chassis_index, 21, 1e-5)  # time step

    assert execution.real_initial_value(wheel_index, 13, 40)  # mass
    assert execution.string_initial_value(wheel_index, 1, "Euler")  # solver
    assert execution.real_initial_value(wheel_index, 28, 1e-5)  # time step

    assert execution.simulate_until(4 * 1e9)

    from_step = 0
    sample_count = 500000

    _, _, chassis_v_out_values = observer.time_series_real_samples(
        chassis_index, value_reference=chassis_v_out, sample_count=sample_count, from_step=from_step
    )

    _, _, chassis_f_in_values = observer.time_series_real_samples(
        chassis_index, value_reference=chassis_f_in, sample_count=sample_count, from_step=from_step
    )

    _, _, wheel_f_out_values = observer.time_series_real_samples(
        wheel_index, value_reference=wheel_f_out, sample_count=sample_count, from_step=from_step
    )

    _, _, wheel_v_in_values = observer.time_series_real_samples(
        wheel_index, value_reference=wheel_v_in, sample_count=sample_count, from_step=from_step
    )

    result = [
        abs(v1 * u1 - v2 * u2)
        for v1, u1, v2, u2 in zip(chassis_v_out_values, chassis_f_in_values, wheel_f_out_values, wheel_v_in_values)
    ]

    for x in result[-100:]:
        assert x < 1e-2
