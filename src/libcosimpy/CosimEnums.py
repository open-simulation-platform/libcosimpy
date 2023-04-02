from enum import Enum


class CosimVariableCausality(Enum):
    """
    Enum for variable causality
    """
    INPUT = 0
    PARAMETER = 1
    OUTPUT = 2
    CALCULATED_PARAMETER = 3
    LOCAL = 4
    INDEPENDENT = 5


class CosimVariableVariability(Enum):
    """
    Enum for variable variability
    """
    CONSTANT = 0
    FIXED = 1
    TUNABLE = 2
    DISCRETE = 3
    CONTINUOUS = 4


class CosimVariableType(Enum):
    """
    Enum for variable type
    """
    REAL = 0
    INTEGER = 1
    STRING = 2
    BOOLEAN = 3


class CosimErrorCode(Enum):
    """
    Enum for library error codes
    """
    NONE = -1  # Undefined
    SUCCESS = 0  # No issues
    UNSPECIFIED = 1
    ERRNO = 2  # C/C++ runtime error
    INVALID_ARGUMENT = 3
    ILLEGAL_STATE = 4
    OUT_OF_RANGE = 5  # Index out of range
    STEP_TOO_LONG = 6  # Step failed, can be retried with shorter step length (if supported by all slaves)
    BAD_FILE = 7  # Corrupt or invalid file
    UNSUPPORTED_FEATURE = 8  # Requested feature is not supported (e.g. an FMI feature)
    DL_LOAD_ERROR = 9  # Error loading dynamic library (e.g. model code)
    MODEL_ERROR = 10  # Model reported error
    ZIP_ERROR = 11  # ZIP file error


class CosimExecutionState(Enum):
    """
    Enum for execution simulation states
    """
    STOPPED = 0
    RUNNING = 1
    ERROR = 2
