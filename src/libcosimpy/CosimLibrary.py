import warnings
from ctypes import cdll
import os

# Path of libcosimc .dll (Windows) or .so (Linux) files
lib_path = os.path.dirname(os.path.realpath(__file__))
try:
    if os.name == 'nt':
        lib = cdll.LoadLibrary(f'{lib_path}/libcosimc/cosimc.dll')
    else:
        lib = cdll.LoadLibrary(f'{lib_path}/libcosimc/libcosimc.so')
except FileNotFoundError:
    warnings.warn('Unable to load cosimc library, searching in the default search paths..')
    if os.name == 'nt':
        lib = cdll.LoadLibrary(f'cosimc.dll')
    else:
        lib = cdll.LoadLibrary(f'libcosimc.so')


