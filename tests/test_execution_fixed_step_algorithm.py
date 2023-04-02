from pytest import raises
from libcosimpy.CosimExecution import CosimExecution
from libcosimpy.CosimEnums import CosimExecutionState, CosimErrorCode


def test_from_step_size_float():
    execution = CosimExecution.from_step_size(step_size=1e3)
    execution_status = execution.execution_status
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    assert CosimErrorCode(execution_status.error_code) == CosimErrorCode.SUCCESS


def test_from_step_size_int():
    execution = CosimExecution.from_step_size(step_size=1000)
    execution_status = execution.execution_status
    assert CosimExecutionState(execution_status.state) == CosimExecutionState.STOPPED
    assert CosimErrorCode(execution_status.error_code) == CosimErrorCode.SUCCESS


def test_step_size_negative():
    with raises(AssertionError) as e_info:
        CosimExecution.from_step_size(step_size=-1e3)
        assert "positive" in str(e_info.value)


def test_step_size_zero():
    with raises(AssertionError) as e_info:
        CosimExecution.from_step_size(step_size=0)
        assert "non-zero" in str(e_info.value)


def test_step_size_string_double():
    with raises(TypeError) as e_info:
        CosimExecution.from_step_size(step_size="1e3")
        assert "convertible" in str(e_info.value)


def test_step_size_string_int():
    with raises(TypeError) as e_info:
        CosimExecution.from_step_size(step_size="1000")
        assert "convertible" in str(e_info.value)


def test_step_size_none():
    with raises(TypeError) as e_info:
        CosimExecution.from_step_size(step_size=None)
        assert "convertible" in str(e_info.value)
