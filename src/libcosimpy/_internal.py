import ctypes


def wrap_function(lib: ctypes.CDLL, funcname: str, restype, argtypes: list[ctypes]):
    """Simplify wrapping ctypes functions"""
    func = lib.__getattr__(funcname)
    func.restype = restype
    func.argtypes = argtypes
    return func


class CTypeMeta(type(ctypes.Structure)):
    def __new__(cls, name, bases, namespace):
        annotations = namespace.get("__annotations__", {})
        namespace["_fields_"] = list(annotations.items())
        return super().__new__(cls, name, bases, namespace)
