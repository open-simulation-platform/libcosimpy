from pytest import raises
from libcosimpy.CosimExecution import CosimExecution
from libcosimpy.CosimEnums import CosimExecutionState, CosimErrorCode


def test_from_osp_file(test_dir):
    execution = CosimExecution.from_osp_config_file(osp_path=f"{test_dir}/data/msmi")
    execution_status = execution.execution_status
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    assert CosimErrorCode(execution_status.error_code) == CosimErrorCode.SUCCESS
    assert execution.num_slaves() == 4
    slave_infos = execution.slave_infos()
    knuckle_boom_crane = slave_infos[0]
    crane_controller = slave_infos[1]
    true_identity = slave_infos[2]
    one_identity = slave_infos[3]
    name_set = {
        knuckle_boom_crane.name.decode(),
        crane_controller.name.decode(),
        true_identity.name.decode(),
        one_identity.name.decode(),
    }
    assert name_set == {
        "KnuckleBoomCrane",
        "CraneController",
        "TrueIdentity",
        "OneIdentity",
    }


def test_from_osp_file_invalid(test_dir):
    with raises(AssertionError) as e_info:
        CosimExecution.from_osp_config_file(osp_path=f"{test_dir}/data/nonexisting")
        assert "path" in str(e_info.value)


def test_from_osp_file_none():
    with raises(AttributeError) as e_info:
        CosimExecution.from_osp_config_file(osp_path=None)
        assert "encode" in str(e_info.value)


def test_from_osp_file_not_a_path():
    with raises(AssertionError) as e_info:
        CosimExecution.from_osp_config_file(osp_path="not a valid path")
        assert "path" in str(e_info.value)


def test_from_osp_file_invalid_type():
    with raises(AttributeError) as e_info:
        CosimExecution.from_osp_config_file(osp_path=0)
        assert "encode" in str(e_info.value)
