from typing import Any
import inspect
import os
import platform

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class WheelHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        super().initialize(version, build_data)
        config_settings: dict[str, Any] = {}
        system_os = platform.system()
        build_data["infer_tag"] = True
        build_data["pure_python"] = False

        os.system("conan remote add osp https://osp.jfrog.io/artifactory/api/conan/conan-local --force")
        os.system("conan profile detect --force")

        for frame_info in inspect.stack():
            frame = frame_info.frame
            module = inspect.getmodule(frame)
            if module and module.__name__.startswith("hatchling.build") and "config_settings" in frame.f_locals:
                config_settings = frame.f_locals["config_settings"] or {}

        package_list = config_settings.get("CONAN_BUILD")
        if package_list:
            build_packages = " ".join([f"-b {p}/*" for p in package_list.split(",")])
        else:
            build_packages = "-b missing"

        assert (
            os.system(f"conan install . -u {build_packages} -of build --format json -b b2/* --out-file graph.json") == 0
        ), "Conan install failed"

        if "CONAN_UPLOAD_OSP" in os.environ:
            print("Uploading packages..")
            os.system("conan list --graph=graph.json --format=json > pkglist.json")
            os.system("conan upload --confirm --list=pkglist.json --remote osp")

        if system_os == "Linux":
            os.system("patchelf --set-rpath '$ORIGIN' build/libcosimc/*")
