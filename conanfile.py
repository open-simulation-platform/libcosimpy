from conan import ConanFile
from conan.tools.files import copy


class LibCosimpyConanDependency(ConanFile):
    name = "libcosimpy-recipe"
    default_options = {
        "libcosim/*:proxyfmu": True,
    }

    def requirements(self):
        self.tool_requires("cmake/[>=4.0]")
        self.requires("libcosimc/0.11.2@osp/stable")

    def configure(self):
        self.options["*"].shared = False
        self.options["libcosimc/*"].shared = True

    def generate(self):
        for dep in self.dependencies.values():
            for dep_bin_dir in dep.cpp_info.bindirs:
                copy(self, "*.dll", src=dep_bin_dir, dst="libcosimc", keep_path=False)
            for dep_lib_dir in dep.cpp_info.libdirs:
                copy(self, "*.so.*", src=dep_lib_dir, dst="libcosimc", keep_path=False)
                copy(self, "*.so", src=dep_lib_dir, dst="libcosimc", keep_path=False)
