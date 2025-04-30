from pytest import raises
from libcosimpy.CosimExecution import CosimExecution
from libcosimpy.CosimEnums import CosimExecutionState, CosimErrorCode


def test_from_ssp_file(test_dir: str):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo")
    execution_status = execution.execution_status
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    assert CosimErrorCode(execution_status.error_code) == CosimErrorCode.SUCCESS
    assert execution.num_slaves() == 2
    slave_infos = execution.slave_infos()
    knuckle_boom_crane = slave_infos[0]
    crane_controller = slave_infos[1]
    name_set = {knuckle_boom_crane.name.decode(), crane_controller.name.decode()}
    assert name_set == {"KnuckleBoomCrane", "CraneController"}


def test_from_ssp_file_with_step_size(test_dir: str):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo", step_size=1000)
    execution_status = execution.execution_status
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    assert CosimErrorCode(execution_status.error_code) == CosimErrorCode.SUCCESS
    assert execution.num_slaves() == 2
    slave_infos = execution.slave_infos()
    knuckle_boom_crane = slave_infos[0]
    crane_controller = slave_infos[1]
    name_set = {knuckle_boom_crane.name.decode(), crane_controller.name.decode()}
    assert name_set == {"KnuckleBoomCrane", "CraneController"}


def test_from_ssp_file_with_step_size_float(test_dir: str):
    execution = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo", step_size=1e3)
    execution_status = execution.execution_status
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    assert CosimErrorCode(execution_status.error_code) == CosimErrorCode.SUCCESS
    assert execution.num_slaves() == 2
    slave_infos = execution.slave_infos()
    knuckle_boom_crane = slave_infos[0]
    crane_controller = slave_infos[1]
    assert knuckle_boom_crane.name.decode() == "KnuckleBoomCrane"
    assert crane_controller.name.decode() == "CraneController"


def test_step_size_negative(test_dir: str):
    with raises(AssertionError) as e_info:
        _ = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo", step_size=-1)
        assert "positive" in str(e_info.value)


def test_step_size_zero(test_dir: str):
    with raises(AssertionError) as e_info:
        _ = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo", step_size=0)
        assert "non-zero" in str(e_info.value)


def test_step_size_string(test_dir: str):
    with raises(ValueError) as e_info:
        _ = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/ssp/demo", step_size="invalid")  # pyright: ignore
        assert "convertible" in str(e_info.value)


def test_from_ssp_file_invalid(test_dir: str):
    with raises(AssertionError) as e_info:
        _ = CosimExecution.from_ssp_file(ssp_path=f"{test_dir}/data/nonexisting")
        assert "path" in str(e_info.value)


def test_from_ssp_file_none():
    with raises(AttributeError) as e_info:
        _ = CosimExecution.from_ssp_file(ssp_path=None)  # pyright: ignore
        assert "encode" in str(e_info.value)


def test_from_osp_file_not_a_path():
    with raises(AssertionError) as e_info:
        _ = CosimExecution.from_ssp_file(ssp_path="not a valid path")
        assert "path" in str(e_info.value)


def test_from_osp_file_invalid_type():
    with raises(AttributeError) as e_info:
        _ = CosimExecution.from_ssp_file(ssp_path=0)  # pyright: ignore
        assert "encode" in str(e_info.value)
