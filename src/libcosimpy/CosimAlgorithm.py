from ctypes import (
    Structure,
    POINTER,
    c_double,
)
from dataclasses import dataclass
from typing import Optional

from . import CosimLibrary
from ._internal import CTypeMeta, wrap_function


@dataclass
class EccoParams(Structure, metaclass=CTypeMeta):
    safety_factor: c_double = c_double(0.8)
    step_size: c_double = c_double(0.01)
    min_step_size: c_double = c_double(1e-4)
    max_step_size: c_double = c_double(1e-4)
    min_change_rate: c_double = c_double(0.01)
    max_change_rate: c_double = c_double(0.2)
    abs_tolerance: c_double = c_double(1e-4)
    rel_tolerance: c_double = c_double(1e-4)
    p_gain: c_double = c_double(0.2)
    i_gain: c_double = c_double(0.15)


class CosimAlgorithm(Structure):
    __create_key: object = object()
    __ptr: Optional["CosimAlgorithm"] = None

    def __init__(
        self,
        create_key: object = None,
        algorithm_ptr: Optional[POINTER("CosimAlgorithm")] = None,
    ):
        """
        Creates a co-sim algorithm

        :param object create_key: Used internally in the object to determine origin of constructor call
        :param POINTER(CosimAlgorithm) algorithm_ptr: Pointer to object created by classmethod
        :return: CosimAlgorithm object
        """
        super().__init__()

        self.__ptr = algorithm_ptr

        # Constructor should only be called using a classmethod
        assert create_key is not CosimAlgorithm.__create_key, (
            "Execution can only be initialized using the CosimAlgorithm.create"
        )

    @classmethod
    def create_ecco_algorithm(cls, param: EccoParams) -> "CosimAlgorithm":
        ecco_algorithm_create = wrap_function(
            lib=CosimLibrary.lib,
            funcname="cosim_ecco_algorithm_create",
            argtypes=[
                c_double,
                c_double,
                c_double,
                c_double,
                c_double,
                c_double,
                c_double,
                c_double,
                c_double,
                c_double,
            ],
            restype=POINTER(CosimAlgorithm),
        )

        ecco_algorithm_ptr = ecco_algorithm_create(
            param.safety_factor,
            param.step_size,
            param.min_step_size,
            param.max_step_size,
            param.min_change_rate,
            param.max_change_rate,
            param.abs_tolerance,
            param.rel_tolerance,
            param.p_gain,
            param.i_gain,
        )

        return cls(cls.__create_key, ecco_algorithm_ptr)
