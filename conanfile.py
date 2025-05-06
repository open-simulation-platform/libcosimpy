from conan import ConanFile
from conan.tools.files import copy


class LibCosimpyConanDependency(ConanFile):
    name = "libcosimpy-recipe"
    requires = "libcosimc/0.11.0@osp/stable"
    default_options = {
        "libcosim/*:proxyfmu": True,
    }

    def generate(self):
        for dep in self.dependencies.values():
            for dep_bin_dir in dep.cpp_info.bindirs:
                copy(self, "*.dll", src=dep_bin_dir, dst="libcosimc", keep_path=False)
            for dep_lib_dir in dep.cpp_info.libdirs:
                copy(self, "*.so.*", src=dep_lib_dir, dst="libcosimc", keep_path=False)
                copy(self, "*.so", src=dep_lib_dir, dst="libcosimc", keep_path=False)
