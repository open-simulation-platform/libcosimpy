from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from conan.api.conan_api import ConanAPI
from conan.cli.cli import Cli
import os
import platform


class WheelHook(BuildHookInterface):
    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        super().initialize(version, build_data)
        build_data["infer_tag"] = True
        build_data["pure_python"] = False
        system_os = platform.system()
        api = ConanAPI()
        cli = Cli(api)
        cli.add_commands()
        api.command.cli = cli
        lockfile = "conan/conan-linux64.lock" if system_os == "Linux" else "conan/conan-win64.lock"
        api.command.run("remote add osp https://osp.jfrog.io/artifactory/api/conan/conan-local --force --index 0")
        api.command.run(f"install conan -b missing --lockfile {lockfile}")
        
        if system_os == "Linux":
            os.system("patchelf --set-rpath '$ORIGIN' build/libcosimc/*")
