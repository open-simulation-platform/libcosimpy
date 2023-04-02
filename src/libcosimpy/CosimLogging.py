from ctypes import c_int
from . import Wrapper
from . import CosimLibrary

from enum import Enum


class CosimLogLevel(Enum):
    """
    Enum log levels in C library
    """
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    FATAL = 5


def log_output_level(log_level):
    """
    Sets the output log level of the libcosimc library

    :param CosimLogLevel log_level:
    """
    log_output_level_set = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_log_set_output_level',
                                                 argtypes=[c_int],
                                                 restype=None)
    log_output_level_set(log_level.value)
