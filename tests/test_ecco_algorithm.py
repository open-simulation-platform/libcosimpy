from libcosimpy.CosimAlgorithm import CosimAlgorithm, EccoParams


def test_ecco_algorithm_create():
    params = EccoParams()
    ecco_algorithm = CosimAlgorithm.create_ecco_algorithm(params)
    assert ecco_algorithm is not None