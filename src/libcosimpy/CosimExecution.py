from ctypes import Structure, c_int, POINTER, c_int64, c_char_p, c_bool, c_double, pointer, c_size_t, c_uint32
from . import Wrapper
from . import CosimLibrary
from . import CosimManipulator
from . import CosimSlave
from . import CosimObserver
from . import CosimConstants
from . import CosimEnums


class CosimExecution(Structure):
    """
    A cosim execution object to hold and run simulation configurations. Object initialized with classmethods with .from
    """
    # Key used to ensure the constructor can only be called from classmethods
    __create_key = object()

    def __init__(self, create_key=None, execution_ptr=None):
        """
        Creates CosimObserver from classmethod calls starting with .from

        :param object create_key: Used internally in the object to determine origin of constructor call
        :param POINTER(CosimExecution) execution_ptr: Pointer to object created by classmethod
        :return: CosimObserver object
        """
        # Store the pointer used by the C library
        self.__ptr = execution_ptr

        # Constructor should only be called using a classmethod
        assert (create_key == CosimExecution.__create_key), \
            "Execution can only be initialized using the CosimExecution.from"

        # Pointer to be passed to C function when requesting status updates
        self.execution_status = CosimExecutionStatus()
        self.__execution_status_ptr = pointer(self.execution_status)

        self.__multiple_steps = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_step',
                                                      argtypes=[POINTER(CosimExecution), c_int64],
                                                      restype=None)
        self.__add_local_slave = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_add_slave',
                                                       argtypes=[POINTER(CosimExecution),
                                                                 POINTER(CosimSlave.CosimLocalSlave)],
                                                       restype=c_int)
        self.__simulate_until = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_simulate_until',
                                                      argtypes=[POINTER(CosimExecution), c_int64], restype=c_int)
        self.__stop = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_stop',
                                            argtypes=[POINTER(CosimExecution)],
                                            restype=c_int)
        self.__enable_real_time_simulation = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                                   funcname='cosim_execution_enable_real_time_simulation',
                                                                   argtypes=[POINTER(CosimExecution)],
                                                                   restype=c_int)
        self.__disable_real_time_simulation = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                                    funcname='cosim_execution_disable_real_time_simulation',
                                                                    argtypes=[POINTER(CosimExecution)],
                                                                    restype=c_int)
        self.__real_time_factor_target = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                               funcname='cosim_execution_set_real_time_factor_target',
                                                               argtypes=[POINTER(CosimExecution), c_double],
                                                               restype=c_int)
        self.__steps_to_monitor = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                        funcname='cosim_execution_set_steps_to_monitor',
                                                        argtypes=[POINTER(CosimExecution), c_int],
                                                        restype=c_int)
        self.__add_manipulator = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_add_manipulator',
                                                       argtypes=[POINTER(CosimExecution),
                                                                 POINTER(CosimManipulator.CosimManipulator)],
                                                       restype=c_int)
        self.__add_observer = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_add_observer',
                                                    argtypes=[POINTER(CosimExecution),
                                                              POINTER(CosimObserver.CosimObserver)],
                                                    restype=c_int)
        self.__status = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_get_status',
                                              argtypes=[POINTER(CosimExecution), POINTER(CosimExecutionStatus)],
                                              restype=c_int)
        self.__slave_num_variables = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                           funcname='cosim_slave_get_num_variables',
                                                           argtypes=[POINTER(CosimExecution), c_int],
                                                           restype=c_int)
        self.__num_modified_variables = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                              funcname='cosim_get_num_modified_variables',
                                                              argtypes=[POINTER(CosimExecution)],
                                                              restype=c_int)
        self.__load_scenario = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_load_scenario',
                                                     argtypes=[POINTER(CosimExecution),
                                                               POINTER(CosimManipulator.CosimManipulator),
                                                               c_char_p],
                                                     restype=c_int)
        self.__real_initial = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                    funcname='cosim_execution_set_real_initial_value',
                                                    argtypes=[POINTER(CosimExecution),
                                                              c_int,
                                                              c_uint32,
                                                              c_double],
                                                    restype=c_int)
        self.__integer_initial = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                       funcname='cosim_execution_set_integer_initial_value',
                                                       argtypes=[POINTER(CosimExecution),
                                                                 c_int,
                                                                 c_uint32,
                                                                 c_int],
                                                       restype=c_int)

        self.__boolean_initial = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                       funcname='cosim_execution_set_boolean_initial_value',
                                                       argtypes=[POINTER(CosimExecution),
                                                                 c_int,
                                                                 c_uint32,
                                                                 c_bool],
                                                       restype=c_int)

        self.__string_initial = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                      funcname='cosim_execution_set_string_initial_value',
                                                      argtypes=[POINTER(CosimExecution),
                                                                c_int,
                                                                c_uint32,
                                                                c_char_p],
                                                      restype=c_int)

    @classmethod
    def from_step_size(cls, step_size):
        """
        Creates empty execution based on step size

        :param step_size: Step size in nanos
        :return: CosimExecution object
        """
        try:
            step_size_int = int(step_size)
        except TypeError as error:
            raise TypeError("Step size must be an int convertible")
        except ValueError as error:
            try:
                step_size_int = int(float(step_size))
            except ValueError as error:
                raise ValueError("Step size must be an int convertible")

        assert (step_size > 0), \
            "Step size must be a positive and non-zero integer"

        execution_create = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_create',
                                                 argtypes=[c_int64, c_int64],
                                                 restype=POINTER(CosimExecution))
        execution_ptr = execution_create(0, step_size_int)
        return cls(cls.__create_key, execution_ptr)

    @classmethod
    def from_osp_config_file(cls, osp_path):
        """
        Creates execution from OspSystemStructure.xml file

        :param str osp_path: Path to .ssd file or OspSystemStructure.xml file
        :return: CosimExecution object
        """
        osp_execution_create = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_osp_config_execution_create',
                                                     argtypes=[c_char_p, c_bool, c_int64],
                                                     restype=POINTER(CosimExecution))
        try:
            encoded_osp_path = osp_path.encode()
        except AttributeError as error:
            raise AttributeError("Unable to encode OSP path")

        execution_ptr = osp_execution_create(encoded_osp_path, False, 0)

        assert execution_ptr, \
            "Unable to create execution from path. Please check if path is correct."

        return cls(cls.__create_key, execution_ptr)

    @classmethod
    def from_ssp_file(cls, ssp_path, step_size=None):
        """
        Creates execution from SystemStructure.ssd file

        :param str ssp_path: Path to .ssd file
        :param int step_size: Optional defined fixed timestep
        :return CosimExecution object
        """
        if step_size is None:
            # Create simulation without defined step size
            ssp_execution_create = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_ssp_execution_create',
                                                         argtypes=[c_char_p, c_bool, c_int64],
                                                         restype=POINTER(CosimExecution))
            execution_ptr = ssp_execution_create(ssp_path.encode(), False, 0)
        else:
            try:
                step_size_int = int(step_size)
            except TypeError as error:
                raise TypeError("Step size must be an int convertible")
            except ValueError as error:
                try:
                    step_size_int = int(float(step_size))
                except ValueError as error:
                    raise ValueError("Step size must be an int convertible")

            assert (step_size > 0), \
                "Step size must be a positive and non-zero integer"

            # Create simulation with defined step size
            ssp_fixed_step_execution_create = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                                    funcname='cosim_ssp_fixed_step_execution_create',
                                                                    argtypes=[c_char_p, c_bool, c_int64, c_int64],
                                                                    restype=POINTER(CosimExecution))
            execution_ptr = ssp_fixed_step_execution_create(ssp_path.encode(), False, 0, step_size_int)

        assert execution_ptr, \
            "Unable to create execution from path. Please check if path is correct."

        return cls(cls.__create_key, execution_ptr)

    def num_slaves(self):
        """
        Number of slaves added and currently connected to execution

        :return: int Number of currently connected slaves
        """
        execution_get_num_slaves = Wrapper.wrap_function(lib=CosimLibrary.lib,
                                                         funcname='cosim_execution_get_num_slaves',
                                                         argtypes=[POINTER(CosimExecution)],
                                                         restype=c_int)
        return execution_get_num_slaves(self.__ptr)

    def start(self):
        """
        Starts and runs the execution until stop() function is called. Status can be polled with status()

        :return: bool Successful start of execution
        """
        execution_start = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_start',
                                                argtypes=[POINTER(CosimExecution)],
                                                restype=c_int)
        return execution_start(self.__ptr) == CosimConstants.success

    def stop(self):
        """
        Stop the simulation initialized by the start() function

        :return: bool Successful stop of execution
        """
        return self.__stop(self.__ptr) == CosimConstants.success

    def simulate_until(self, target_time):
        """
        Starts and automatically stops the simulation once target time is reached

        :param int target_time: End of simulation time in nanos
        :return: bool Successful simulation until target time
        """
        try:
            target_time_int = int(target_time)
        except TypeError as error:
            raise TypeError("Target time must be an int convertible")
        except ValueError as error:
            try:
                target_time_int = int(float(target_time))
            except ValueError as error:
                raise ValueError("Target time must be an int convertible")

        assert (target_time_int > 0), \
            "Target time must be a positive and non-zero integer"
        return self.__simulate_until(self.__ptr, target_time_int) != CosimConstants.failure

    def step(self, step_count=1):
        """
        Advance the simulation for 1 or multiple steps

        :param int step_count: Number of steps to advance with default of 1
        :return: bool Successful step execution
        """
        return self.__multiple_steps(self.__ptr, step_count) == CosimConstants.success

    def real_time_simulation_enabled(self, enabled=True):
        """
        Enables or disables real time simulation for the execution

        :param bool enabled: Boolean for toggling desired real time state
        :return: bool Successfully set real time state to desired value
        """
        if enabled:
            return self.__enable_real_time_simulation(self.__ptr) == CosimConstants.success
        else:
            return self.__disable_real_time_simulation(self.__ptr) == CosimConstants.success

    def real_time_factor_target(self, real_time_factor):
        """
        Set custom real time factor target

        :param float real_time_factor: Real time factor
        :return: bool Successfully set real time factor
        """
        return self.__real_time_factor_target(self.__ptr, float(real_time_factor)) == CosimConstants.success

    def steps_to_monitor(self, step_count):
        """
        Steps to monitor for rolling average real time factor measurement

        :param int step_count: Size of window
        :return: bool Successfully set number of steps
        """
        assert (step_count > 0), \
            "Step count must be a positive and non-zero integer"

        return self.__steps_to_monitor(self.__ptr, step_count) == CosimConstants.success

    def add_manipulator(self, manipulator):
        """
        Adds manipulator to execution

        :param CosimManipulator manipulator: Manipulator to be added
        :return: bool Successfully added manipulator to execution
        """
        return self.__add_manipulator(self.__ptr, manipulator.ptr()) == CosimConstants.success

    def add_observer(self, observer):
        """
        Add observer to execution

        :param CosimObserver observer: Observer to be added to the simulation
        :return: bool Successfully added observer to execution
        """
        return self.__add_observer(self.__ptr, observer.ptr()) == CosimConstants.success

    def load_scenario(self, manipulator, scenario_file):
        """
        Loads and executes scenario from file

        :param CosimManipulator manipulator: Manipulator to be used with the scenario
        :param str scenario_file: Path to JSON file describing the scenario
        :return: bool Successfully loaded scenario
        """
        try:
            encoded_path = scenario_file.encode()
        except AttributeError as error:
            raise AttributeError("Unable to encode scenario path file")

        return self.__load_scenario(self.__ptr, manipulator.ptr(), encoded_path) == CosimConstants.success

    def status(self):
        """
        Returns current execution status as status object

        :return: CosimExecutionStatus object
        """
        self.__status(self.__ptr, self.__execution_status_ptr)
        return self.execution_status

    def slave_infos(self):
        """
        Returns list of CosimSlaveInfo objects for all slaves

        :return: CosimSlaveInfo list of length num_slaves()
        """
        slave_count = self.num_slaves()
        slave_infos_list = (CosimSlave.CosimSlaveInfo * slave_count)()
        slave_infos = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_get_slave_infos',
                                            argtypes=[POINTER(CosimExecution), CosimSlave.CosimSlaveInfo * slave_count,
                                                      c_size_t],
                                            restype=c_int)
        slave_infos(self.__ptr, slave_infos_list, slave_count)
        return slave_infos_list

    def add_local_slave(self, local_slave):
        """
        Add local slave to execution

        :param CosimLocalSlave local_slave: Local slave to be added to the execution
        :return: int Index of the slave that has been added
        """
        return self.__add_local_slave(self.__ptr, local_slave.ptr())

    def slave_index_from_instance_name(self, instance_name):
        """
        Returns the slave index from instance name or None if no slave with no slave with instance name was found

        :param str instance_name: Name of instance
        :return: int Slave index of instance with specific name
        """
        slave_infos_list = self.slave_infos()
        for slave_info in slave_infos_list:
            if slave_info.name == instance_name.encode():
                return slave_info.index
        return None

    def num_slave_variables(self, slave_index):
        """
        Returns total number of variables for a slave

        :param int slave_index: Index of the slave
        :return: int Number of variables for a slave
        """
        return self.__slave_num_variables(self.__ptr, slave_index)

    def slave_variables(self, slave_index):
        """
        Return variable metadata form slave

        :param int slave_index: Index of the slave
        :return: List of CosimSlaveVariableDescription variables of size num_slave_variables(slave_index)
        """
        slave_variables_count = self.num_slave_variables(slave_index)
        slave_variables_list = (CosimSlave.CosimSlaveVariableDescription * slave_variables_count)()
        slave_variables = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_slave_get_variables',
                                                argtypes=[POINTER(CosimExecution), c_int,
                                                          CosimSlave.CosimSlaveVariableDescription * slave_variables_count,
                                                          c_size_t],
                                                restype=c_int)
        slave_variables(self.__ptr, slave_index, slave_variables_list, slave_variables_count)
        return slave_variables_list

    def real_initial_value(self, slave_index, variable_reference, value):
        """
        Set initial value for variable of type real

        :param int slave_index: Index of the slave
        :param int variable_reference: Index of the variable of the slave
        :param float value: Value to be set as initial value
        :return: bool Successfully set initial value
        """
        return self.__real_initial(self.__ptr, slave_index, variable_reference, value) == CosimConstants.success

    def integer_initial_value(self, slave_index, variable_reference, value):
        """
        Set initial value for variable of type integer

        :param int slave_index: Index of the slave
        :param int variable_reference: Index of the variable of the slave
        :param int value: Value to be set as initial value
        :return: bool Successfully set initial value
        """
        return self.__integer_initial(self.__ptr, slave_index, variable_reference, value) == CosimConstants.success

    def boolean_initial_value(self, slave_index, variable_reference, value):
        """
        Set initial value for variable of type boolean

        :param int slave_index: Index of the slave
        :param int variable_reference: Index of the variable of the slave
        :param bool value: Value to be set as initial value
        :return: bool Successfully set initial value
        """
        return self.__boolean_initial(self.__ptr, slave_index, variable_reference, value) == CosimConstants.success

    def string_initial_value(self, slave_index, variable_reference, value):
        """
        Set initial value for variable of type string

        :param int slave_index: Index of the slave
        :param int variable_reference: Index of the variable of the slave
        :param float value: Value to be set as initial value
        :return: bool Successfully set initial value
        """
        return self.__string_initial(self.__ptr, slave_index, variable_reference,
                                     value.encode()) == CosimConstants.success

    def __del__(self):
        """
        Releases C objects when CosimExecution is deleted in python
        """
        # Release object in C when object is removed (if pointer exists)
        if self.__ptr is not None:
            execution_destroy = Wrapper.wrap_function(lib=CosimLibrary.lib, funcname='cosim_execution_destroy',
                                                      argtypes=[POINTER(CosimExecution)], restype=c_int)
            execution_destroy(self.__ptr)


class CosimExecutionStatus(Structure):
    """
    Object holding the status of an execution
    """
    _fields_ = [
        ('current_time', c_int64), ('state', c_int), ('error_code', c_int), ('real_time_factor', c_double),
        ('rolling_average_real_time_factor', c_double), ('real_time_factor_target', c_double),
        ('is_real_time_simulation', c_int),
        ('steps_to_monitor', c_int)
    ]

    def __repr__(self):
        return 'current_time: {0}, state: {1}, error_code: {2}, real_time_factor: {3}, real_time_factor_target: {4}, ' \
               'rolling_average_real_time_factor: {5}, is_real_time_simulation: {6}, steps_to_monitor: {7}'.format(
                self.current_time,
                CosimEnums.CosimExecutionState(self.state),
                CosimEnums.CosimErrorCode(self.error_code),
                self.real_time_factor,
                self.real_time_factor_target,
                self.rolling_average_real_time_factor,
                self.is_real_time_simulation,
                self.steps_to_monitor)
