import ctypes
from typing import Any


from libcosimpy import CosimLibrary


def wrap_function(lib: ctypes.CDLL, funcname: str, restype: Any, argtypes: list[Any]):
    """Simplify wrapping ctypes functions"""
    func = lib.__getattr__(funcname)
    func.restype = restype
    func.argtypes = argtypes
    return func


class CTypeMeta(type(ctypes.Structure)):
    def __new__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]):
        annotations = namespace.get("__annotations__", {})
        namespace["_fields_"] = list(annotations.items())
        return super().__new__(cls, name, bases, namespace)


def get_last_error_message() -> str:
    cosim_last_error_message = wrap_function(
        lib=CosimLibrary.lib,
        funcname="cosim_last_error_message",
        argtypes=[],
        restype=ctypes.c_char_p,
    )
    return cosim_last_error_message().decode("utf-8")
