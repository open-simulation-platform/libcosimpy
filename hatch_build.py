from typing import Any
import os
import platform

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class WheelHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        super().initialize(version, build_data)
        # build_data["infer_tag"] = False
        # build_data["pure_python"] = False
        system_os = platform.system()
        os.system("conan remote add osp https://osp.jfrog.io/artifactory/api/conan/conan-local --force --index 0")
        os.system("conan profile detect --force")
        os.system("conan install -u -b missing -of build .")
        if system_os == "Linux":
            os.system("patchelf --set-rpath '$ORIGIN' build/libcosimc/*")
