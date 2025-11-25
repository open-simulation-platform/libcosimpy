from libcosimpy._internal import libcosimc


def test_load_libray():
    assert libcosimc() is not None
