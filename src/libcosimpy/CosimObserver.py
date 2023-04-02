from ctypes import Structure, c_int64, POINTER, c_char_p, c_int, c_uint32, c_longlong, c_double, c_size_t, c_bool
from . import CosimLibrary
from . import Wrapper
from . import CosimConstants


class CosimObserver(Structure):
    """
    Observer used for monitoring and logging values from simulations
    """
    # Key used to ensure the constructor can only be called from classmethods
    __create_key = object()

    def __init__(self, create_key=None, observer_ptr=None):
        """
        Creates CosimObserver from classmethod calls starting with .create

        :param object create_key: Used internally in the object to determine origin of constructor call
        :param POINTER(CosimObserver) observer_ptr: Pointer to object created by classmethod
        :return: CosimObserver object
        """
        # Constructor should only be called using a classmethod
        assert (create_key == CosimObserver.__create_key), \
            "Observer can only be initialized using the CosimExecution.create"
        # Store the pointer used by the C library
        self.__ptr = observer_ptr
        self.__step_numbers = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_observer_get_step_numbers',
                                                    argtypes=[POINTER(CosimObserver), c_longlong, c_longlong, c_uint32],
                                                    restype=c_int)
        self.__start_observing = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_observer_start_observing',
                                                       argtypes=[POINTER(CosimObserver), c_int, c_int, c_uint32],
                                                       restype=c_int)
        self.__stop_observing = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_observer_stop_observing',
                                                      argtypes=[POINTER(CosimObserver), c_int, c_int, c_uint32],
                                                      restype=c_int)

    @classmethod
    def create_last_value(cls):
        """
        Creates observer storing last value for all variables

        :return: CosimObserver object from constructor
        """
        last_value_observer_create = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                           funcname='cosim_last_value_observer_create', argtypes=[],
                                                           restype=POINTER(CosimObserver))
        observer_ptr = last_value_observer_create()
        return cls(cls.__create_key, observer_ptr)

    @classmethod
    def create_to_dir(cls, log_dir):
        """
        Creates observer with specified logging directory

        :param str log_dir: Directory of output log files
        :return: CosimObserver object from constructor
        """
        file_observer_create = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_file_observer_create',
                                                     argtypes=[c_char_p],
                                                     restype=POINTER(CosimObserver))
        observer_ptr = file_observer_create(log_dir.encode())
        return cls(cls.__create_key, observer_ptr)

    """@classmethod
    def from_cfg(cls, cfg_path, log_dir):
        
        Creates observer from LogConfig.xml file with specified logging directory

        :param str log_dir: Directory of output log files
        :param str cfg_path: Directory of the LogConfig.xml file
        :return: CosimObserver object from constructor
        
        file_observer_create = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_file_observer_create_from_cfg',
                                                     argtypes=[c_char_p, c_char_p],
                                                     restype=POINTER(CosimObserver))

        observer_ptr = file_observer_create(log_dir.encode(), cfg_path.encode())
        return cls(cls.__create_key, observer_ptr)"""

    @classmethod
    def create_time_series(cls, buffer_size=None):
        """
        Creates observer with memory buffer. Initialized by calling the start_time_series() function

        :param: int size of buffer: Optional specific buffer size for observer
        :return: CosimObserver Object from constructor
        """
        if buffer_size is None:
            time_series_create = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                       funcname='cosim_time_series_observer_create', argtypes=[],
                                                       restype=POINTER(CosimObserver))
            observer_ptr = time_series_create()
            return cls(cls.__create_key, observer_ptr)
        else:
            buffered_time_series_create = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                                funcname='cosim_buffered_time_series_observer_create',
                                                                argtypes=[c_int64], restype=POINTER(CosimObserver))
            observer_ptr = buffered_time_series_create(buffer_size)
            return cls(cls.__create_key, observer_ptr)

    def start_time_series(self, slave_index, value_reference, variable_type):
        """
        Start observing a variable with a time series observer

        :param int slave_index: Index of slave with variable
        :param int value_reference: Reference of variable within slave
        :param CosimVariableType variable_type: Value reference data type
        :return: bool Successfully started observer
        """
        return self.__start_observing(self.__ptr, slave_index, variable_type.value,
                                      value_reference) == CosimConstants.success

    def stop_time_series(self, slave_index, value_reference, variable_type):
        """
        Stop observing a variable with a time series observer

        :param int slave_index: Index of slave with variable
        :param int value_reference: Reference of variable within slave
        :param CosimVariableType variable_type: Value reference data type
        :return: bool Successfully stopped observer
        """
        return self.__stop_observing(self.__ptr, slave_index, variable_type.value,
                                     value_reference) == CosimConstants.success

    def __time_series_samples(self, slave_index, value_reference, sample_count, c_type, from_step):
        """
        Helper function to avoid code duplication for time series sample retrieval
        """
        if c_type == c_double:
            funcname = 'cosim_observer_slave_get_real_samples'
        elif c_type == c_int:
            funcname = 'cosim_observer_slave_get_integer_samples'
        else:
            raise AssertionError("Invalid ctype")
        time_point_array = (c_int64 * sample_count)()
        step_number_array = (c_longlong * sample_count)()
        samples_array = (c_type * sample_count)()

        real_samples = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname=funcname,
                                             argtypes=[POINTER(CosimObserver), c_int,
                                                       c_uint32,
                                                       c_longlong,
                                                       c_size_t,
                                                       c_type * sample_count,
                                                       c_longlong * sample_count,
                                                       c_int64 * sample_count],
                                             restype=c_int64)

        retrieved_samples_count = real_samples(self.__ptr, slave_index, value_reference, from_step, sample_count,
                                               samples_array, step_number_array, time_point_array)
        if retrieved_samples_count < 0:
            raise AssertionError("Unable to retrieve samples. Check if indexes are valid, observer is of type time "
                                 "series and that the time series have been started and at least one step has been "
                                 "executed.")

        # Trim lists to length of number of values
        step_count = sample_count - (step_number_array[:]).count(0)
        return time_point_array[:step_count], step_number_array[:step_count], samples_array[:step_count]

    def time_series_real_samples(self, slave_index, value_reference, from_step, sample_count=10):
        """
        Read real samples from time series observer

        :param int slave_index: Index of slave with variable
        :param int value_reference: Index of the variable of the slave
        :param int from_step: Step when the time series samples is recorded from
        :param int sample_count: Number of samples to take after from_step. Default 10
        :returns list of float: Real value samples. List may be shorter than sample_count
        """
        return self.__time_series_samples(slave_index=slave_index, value_reference=value_reference, from_step=from_step,
                                          sample_count=sample_count, c_type=c_double)

    def time_series_integer_samples(self, slave_index, value_reference, from_step, sample_count=10):
        """
        Read integer samples from time series observer

        :param int slave_index: Index of slave with variable
        :param int value_reference: Index of the variable of the slave
        :param int from_step: Step when the time series samples is recorded from
        :param int sample_count: Number of samples to take after from_step. Default 10
        :returns list of int: Real value samples. List may be shorter than sample_count
        """
        return self.__time_series_samples(slave_index=slave_index, value_reference=value_reference, from_step=from_step,
                                          sample_count=sample_count, c_type=c_int)

    def __last_values(self, slave_index, variable_references, c_type):
        """

        """
        if c_type == c_double:
            funcname = 'cosim_observer_slave_get_real'
        elif c_type == c_int:
            funcname = 'cosim_observer_slave_get_integer'
        elif c_type == c_bool:
            funcname = 'cosim_observer_slave_get_boolean'
        elif c_type == c_char_p:
            funcname = 'cosim_observer_slave_get_string'
        else:
            raise AssertionError("Invalid ctype")

        variable_count = len(variable_references)

        variables_index_array = (c_uint32 * variable_count)(*variable_references)
        value_array = (c_type * variable_count)()

        real_values = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname=funcname,
                                            argtypes=[POINTER(CosimObserver), c_int,
                                                      c_uint32 * variable_count, c_size_t,
                                                      c_type * variable_count],
                                            restype=c_int)

        if real_values(self.__ptr, slave_index, variables_index_array, variable_count,
                       value_array) == CosimConstants.success:
            return value_array[:]
        raise AssertionError("Unable to return values. Check if indexes are valid.")

    def last_real_values(self, slave_index, variable_references):
        """
        Retrieve real values from slave with last value observer

        :param int slave_index: Index of slave with variable
        :param list of int variable_references: List of variable reference indexes
        :returns list of float: Real values from last value observer
        """
        return self.__last_values(slave_index=slave_index, variable_references=variable_references, c_type=c_double)

    def last_integer_values(self, slave_index, variable_references):
        """
        Retrieve integer values from slave with last value observer

        :param int slave_index: Index of slave with variable
        :param list of int variable_references: List of variable reference indexes
        :returns list of int: Integer values from last value observer
        """
        return self.__last_values(slave_index=slave_index, variable_references=variable_references, c_type=c_int)

    def last_boolean_values(self, slave_index, variable_references):
        """
        Retrieve boolean values from slave with last value observer

        :param int slave_index: Index of slave with variable
        :param list of int variable_references: List of variable reference indexes
        :returns list of bool: Boolean values from last value observer
        """
        return self.__last_values(slave_index=slave_index, variable_references=variable_references, c_type=c_bool)

    def last_string_values(self, slave_index, variable_references):
        """
        Retrieve string value from slave with last value observer

        :param int slave_index: Index of slave with variable
        :param list of int variable_references: List of variable reference indexes
        :returns list of string: String values from last value observer
        """
        return self.__last_values(slave_index=slave_index, variable_references=variable_references, c_type=c_char_p)

    def ptr(self):
        """
       Helper function intended to be used by other libcosimc classes
       :return: POINTER(CosimObserver)
       """
        return self.__ptr

    def __del__(self):
        """
        Releases C objects when CosimObserver is deleted in python
        """
        if self.__ptr is not None:
            observer_destroy = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_observer_destroy',
                                                     argtypes=[POINTER(CosimObserver)],
                                                     restype=c_int)
            observer_destroy(self.__ptr)
