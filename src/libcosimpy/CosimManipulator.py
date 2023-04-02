from ctypes import Structure, c_int64, POINTER, c_int, c_uint32, c_size_t, c_double, c_bool, c_char_p
from . import CosimLibrary
from . import Wrapper
from . import CosimConstants


class CosimManipulator(Structure):
    """
    Manipulator used with CosimExecution to edit variables to simulate scenarios
    """
    # Key used to ensure the constructor can only be called from classmethods
    __create_key = object()

    def __init__(self, create_key=None, manipulator_ptr=None):
        """
        Creates CosimManipulator from classmethod calls starting with .create

        :param object create_key: Used internally in the object to determine origin of constructor call
        :param POINTER(CosimManipulator) manipulator_ptr: Pointer to object created by classmethod
        :return: CosimManipulator object
        """
        # Constructor should only be called using a classmethod
        assert (create_key == CosimManipulator.__create_key), \
            "Manipulator can only be initialized using the Cosim.Manipulator.create"
        # Store the pointer used by the C library
        self.__ptr = manipulator_ptr
        """self.__is_scenario_running = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_scenario_is_running',
                                                           argtypes=[POINTER(CosimManipulator)],
                                                           restype=c_int)"""
        self.__abort = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_scenario_abort',
                                             argtypes=[POINTER(CosimManipulator)],
                                             restype=c_int)

    @classmethod
    def create_override(cls):
        """
        Manipulator to override variable values. Classmethod calling the class constructor

        :return: CosimManipulator object from constructor
        """
        override_manipulator_create = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                            funcname='cosim_override_manipulator_create', argtypes=[],
                                                            restype=POINTER(CosimManipulator))
        manipulator_ptr = override_manipulator_create()
        return cls(cls.__create_key, manipulator_ptr)

    @classmethod
    def create_scenario_manager(cls):
        """
        Manipulator to load scenarios from file. Classmethod calling the class constructor

        :return CosimManipulator object from constructor
        """
        scenario_manager_create = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_scenario_manager_create',
                                                        argtypes=[],
                                                        restype=POINTER(CosimManipulator))
        manipulator_ptr = scenario_manager_create()
        return cls(cls.__create_key, manipulator_ptr)

    """def is_scenario_running(self):
        
        Checks if scenario is running

        :return: bool Boolean value describing if the simulation is running or not
        
        return self.__is_scenario_running(self.__ptr) != CosimConstants.failure"""

    def abort_scenario(self):
        """
        Aborts the execution of running scenario

        :return: bool Successfully aborted the scenario
        """
        return self.__abort(self.__ptr) == CosimConstants.success

    def __slave_values(self, slave_index, variable_references, values, c_type):
        """
        Helper function to avoid code duplication for set last value
        """
        if c_type == c_double:
            funcname = 'cosim_manipulator_slave_set_real'
        elif c_type == c_int:
            funcname = 'cosim_manipulator_slave_set_integer'
        elif c_type == c_bool:
            funcname = 'cosim_manipulator_slave_set_boolean'
        elif c_type == c_char_p:
            funcname = 'cosim_manipulator_slave_set_string'
        else:
            raise AssertionError("Invalid ctype")

        variable_count = len(variable_references)

        variable_array = (c_uint32 * variable_count)(*variable_references)
        value_array = (c_type * variable_count)(*values)

        slave_values = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname=funcname,
                                             argtypes=[POINTER(CosimManipulator),
                                                       c_int,
                                                       c_uint32 * variable_count,
                                                       c_size_t,
                                                       c_type * variable_count],
                                             restype=c_int)

        return slave_values(self.__ptr, slave_index, variable_array, variable_count,
                            value_array) == CosimConstants.success

    def slave_real_values(self, slave_index, variable_references, values):
        """
        Set real variables in override manipulator

        :param int slave_index: Index of slave with variable
        :param list of int variable_references: Reference of variable within slave
        :param list of float values: Values to be set for variables in override manipulator
        :return bool Successfully set override values to variables
        """
        return self.__slave_values(slave_index=slave_index, variable_references=variable_references, values=values,
                                   c_type=c_double)

    def slave_integer_values(self, slave_index, variable_references, values):
        """
        Set integer variables in override manipulator

        :param int slave_index: Index of slave with variable
        :param list of int variable_references: Reference of variable within slave
        :param list of int values: Values to be set for variables in override manipulator
        :return bool Successfully set override values to variables
        """
        return self.__slave_values(slave_index=slave_index, variable_references=variable_references, values=values,
                                   c_type=c_int)

    def slave_boolean_values(self, slave_index, variable_references, values):
        """
        Set boolean variables in override manipulator

        :param int slave_index: Index of slave with variable
        :param list of int variable_references: Reference of variable within slave
        :param list of boolean values: Values to be set for variables in override manipulator
        :return bool Successfully set override values to variables
        """
        return self.__slave_values(slave_index=slave_index, variable_references=variable_references, values=values,
                                   c_type=c_bool)

    def slave_string_values(self, slave_index, variable_references, values):
        """
        Set string variables in override manipulator

        :param int slave_index: Index of slave with variable
        :param list of int variable_references: Reference of variable within slave
        :param list of string values: Values to be set for variables in override manipulator
        :return bool Successfully set override values to variables
        """
        return self.__slave_values(slave_index=slave_index, variable_references=variable_references,
                                   values=[v.encode() for v in values], c_type=c_char_p)

    def reset_variables(self, slave_index, variable_type, variable_references):
        """
        Reset variables set by override manipulator

        :param int slave_index: Index of slave with variable
        :param CosimVariableType variable_type: Type of variable to be reset
        :param list of int variable_references: Reference of variable within slave
        :return bool Successful reset of variables
        """
        variable_count = len(variable_references)

        variable_array = (c_uint32 * variable_count)(*variable_references)

        slave_reset = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_manipulator_slave_reset',
                                            argtypes=[POINTER(CosimManipulator),
                                                      c_int,
                                                      c_int,
                                                      c_uint32 * variable_count,
                                                      c_size_t],
                                            restype=c_int)

        return slave_reset(self.__ptr, slave_index, variable_type.value, variable_array, variable_count) == \
               CosimConstants.success

    def ptr(self):
        """
        Helper function intended to be used by other libcosim c classes
        :return: POINTER(CosimManipulator)
        """
        return self.__ptr

    def __del__(self):
        """
        Releases C objects when CosimManipulator is deleted in python
        """
        if self.__ptr is not None:
            manipulator_destroy = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_manipulator_destroy',
                                                        argtypes=[POINTER(CosimManipulator)], restype=c_int64)
            manipulator_destroy(self.__ptr)
