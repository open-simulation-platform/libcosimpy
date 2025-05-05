from __future__ import annotations

import typing
from ctypes import (
    POINTER,
    Structure,
    c_double,
    c_int,
    c_uint32,
)
from dataclasses import dataclass
from typing import Optional

from . import CosimLibrary
from ._internal import wrap_function, get_last_error_message

if typing.TYPE_CHECKING:
    from ctypes import _Pointer  # pyright: ignore[reportPrivateUsage]

    CosimAlgorithmPtr = _Pointer["CosimAlgorithm"]
else:
    CosimAlgorithmPtr = POINTER("CosimAlgorithm")


@dataclass
class EccoParams(Structure):
    """
    Ecco algorithm parameters. See [1] for their detailed descriptions.

    [1] Sadjina, S. and Pedersen, E., 2020. Energy conservation and coupling error reduction in non-iterative
    co-simulations. Engineering with Computers, 36, pp.1579-1587
    """

    safety_factor: float = 0.8
    step_size: float = 0.01
    min_step_size: float = 1e-4
    max_step_size: float = 0.1
    min_change_rate: float = 0.01
    max_change_rate: float = 0.2
    abs_tolerance: float = 1e-4
    rel_tolerance: float = 1e-4
    p_gain: float = 0.2
    i_gain: float = 0.15


class CosimAlgorithm(Structure):
    __create_key: object = object()
    __ptr: Optional[CosimAlgorithmPtr] = None

    def __init__(
        self,
        create_key: object = None,
        algorithm_ptr: Optional[CosimAlgorithmPtr] = None,
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
        assert create_key is CosimAlgorithm.__create_key, (
            "Execution can only be initialized using the CosimAlgorithm.create"
        )

        self.__ecco_add_power_bond = wrap_function(
            lib=CosimLibrary.lib,
            funcname="cosim_ecco_add_power_bond",
            argtypes=[POINTER(CosimAlgorithm), c_int, c_uint32, c_uint32, c_int, c_uint32, c_uint32],
            restype=c_int,
        )

    @classmethod
    def create_ecco_algorithm(cls, param: EccoParams) -> CosimAlgorithm:
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
        if not ecco_algorithm_ptr:
            raise RuntimeError(get_last_error_message())

        return cls(cls.__create_key, ecco_algorithm_ptr)

    def add_power_bond(
        self,
        slave1_index: int,
        slave1_output_reference: int,
        slave1_input_reference: int,
        slave2_index: int,
        slave2_output_reference: int,
        slave2_input_reference: int,
    ) -> int:
        """
        Creates a power bond between two instances of models

        :param slave1_index: Slave index of the first model
        :param slave1_output_reference: An output reference for the first model
        :param slave1_input_reference: An input reference for the first model
        :param slave2_index: Slave index of the second model
        :param slave2_output_reference: An output reference for the second model
        :param slave2_input_reference: An input reference for the second model
        :return: 0 on Success and -1 on error
        """
        return self.__ecco_add_power_bond(
            self.__ptr,
            slave1_index,
            slave1_output_reference,
            slave1_input_reference,
            slave2_index,
            slave2_output_reference,
            slave2_input_reference,
        )

    @property
    def ptr(self) -> Optional[CosimAlgorithmPtr]:
        """
        Returns the pointer to the C object
        """
        return self.__ptr

    def __del__(self):
        """
        Releases C objects when CosimAlgorithm is deleted in python
        """
        # Release object in C when object is removed (if pointer exists)
        if self.__ptr is not None:
            algorithm_destroy = wrap_function(
                lib=CosimLibrary.lib,
                funcname="cosim_algorithm_destroy",
                argtypes=[POINTER(CosimAlgorithm)],
                restype=c_int,
            )
            algorithm_destroy(self.__ptr)
