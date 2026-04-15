import ctypes
from typing import Any
import warnings
from ctypes import cdll
import os


__lib = None


def wrap_function(lib: ctypes.CDLL, funcname: str, restype: Any, argtypes: list[Any]):
    """Simplify wrapping ctypes functions"""
    func = lib.__getattr__(funcname)
    func.restype = restype
    func.argtypes = argtypes
    return func


def libcosimc():
    # Path of libcosimc .dll (Windows) or .so (Linux) files
    global __lib
    if __lib is None:
        lib_path = os.path.dirname(os.path.realpath(__file__))
        try:
            if os.name == "nt":
                __lib = cdll.LoadLibrary(f"{lib_path}/libcosimc/cosimc.dll")
            else:
                __lib = cdll.LoadLibrary(f"{lib_path}/libcosimc/libcosimc.so")
        except FileNotFoundError:
            warnings.warn("Unable to load cosimc library, searching in the default search paths..")
            if os.name == "nt":
                __lib = cdll.LoadLibrary("cosimc.dll")
            else:
                __lib = cdll.LoadLibrary("libcosimc.so")
    return __lib


class CTypeMeta(type(ctypes.Structure)):
    def __new__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]):
        annotations = namespace.get("__annotations__", {})
        namespace["_fields_"] = list(annotations.items())
        return super().__new__(cls, name, bases, namespace)


def get_last_error_message() -> str:
    cosim_last_error_message = wrap_function(
        lib=libcosimc(),
        funcname="cosim_last_error_message",
        argtypes=[],
        restype=ctypes.c_char_p,
    )
    return cosim_last_error_message().decode("utf-8")
