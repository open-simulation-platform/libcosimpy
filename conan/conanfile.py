from conan import ConanFile


class LibCosimpyConanDependency(ConanFile):
    name = "libcosimpy-recipe"
    requires = (
        "libcosimc/0.10.2@osp/stable"
    )

    def imports(self):
        self.copy("*.dll", dst="libcosimc", keep_path=False)
        self.copy("*.so.*", dst="libcosimc", keep_path=False)
        self.copy("*.so", dst="libcosimc", keep_path=False)
