from typing import Any
import os
import platform

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class WheelHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        super().initialize(version, build_data)
        system_os = platform.system()
        os.system("conan remote add osp https://osp.jfrog.io/artifactory/api/conan/conan-local --force")
        os.system("conan profile detect --force")
        assert os.system("conan install . -u -b missing -of build") == 0, "Conan install failed"
        if system_os == "Linux":
            os.system("patchelf --set-rpath '$ORIGIN' build/libcosimc/*")
