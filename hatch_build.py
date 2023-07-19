from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from conans.client.conan_api import Conan
import os
import platform


class WheelHook(BuildHookInterface):
    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        super().initialize(version, build_data)
        build_data["infer_tag"] = True
        build_data["pure_python"] = False
        system_os = platform.system()
        conan, _, _ = Conan.factory()
        conan.config_set("general.revisions_enabled", "True")
        conan.remote_add(remote_name="osp", url="https://osp.jfrog.io/artifactory/api/conan/conan-local", force=True,
                         insert=0)
        conan.install(path="conan",
                      lockfile='conan/conan-linux64.lock' if system_os == "Linux" else 'conan/conan-win64.lock',
                      install_folder="build")
        if system_os == "Linux":
            os.system("patchelf --set-rpath '$ORIGIN' build/libcosimc/*")
