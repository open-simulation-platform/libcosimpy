from ctypes import c_char, c_char_p, POINTER, c_int, Structure, c_uint32
from . import Wrapper
from . import CosimLibrary
from . import CosimConstants
from . import CosimEnums


class CosimSlaveInfo(Structure):
    """
    Name and index of a slave object
    """
    _fields_ = [
        ('name', c_char * CosimConstants.SLAVE_NAME_MAX_SIZE), ('index', c_int)
    ]

    def __repr__(self):
        return 'name: {0}, index: {1}'.format(self.name.decode(), self.index)


class CosimSlaveVariableDescription(Structure):
    """
    Slave variable information object
    """
    _fields_ = [
        ('name', c_char * CosimConstants.SLAVE_NAME_MAX_SIZE), ('reference', c_uint32), ('type', c_int),
        ('causality', c_int),
        ('variability', c_int)
    ]

    def __repr__(self):
        return 'name: {0}, reference: {1}, type: {2}, causality: {3}, variability: {4}' \
            .format(self.name, self.reference, CosimEnums.CosimVariableType(self.type),
                    CosimEnums.CosimVariableCausality(self.causality),
                    CosimEnums.CosimVariableVariability(self.variability))


class CosimLocalSlave(Structure):
    """
    Locally created execution slave
    """
    def __init__(self, fmu_path, instance_name):
        local_slave_create = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_local_slave_create',
                                                   argtypes=[c_char_p, c_char_p],
                                                   restype=POINTER(CosimLocalSlave))
        self.__ptr = local_slave_create(fmu_path.encode(), instance_name.encode())

    def ptr(self):
        """
        Helper function intended to be used by other libcosim c classes
        :return: POINTER(CosimLocalSlave)
        """
        return self.__ptr

    def __del__(self):
        """
        Releases C objects when CosimObserver is deleted in python
        """
        local_slave_destroy = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_local_slave_destroy',
                                                    argtypes=[POINTER(CosimLocalSlave)],
                                                    restype=c_int)
        local_slave_destroy(self.__ptr)
