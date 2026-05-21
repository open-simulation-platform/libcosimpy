from typing import Any
import inspect
import os
import platform
import subprocess
import shlex
import glob

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class WheelHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        super().initialize(version, build_data)
        config_settings: dict[str, Any] = {}
        system_os = platform.system()
        build_data["infer_tag"] = True
        build_data["pure_python"] = False

        subprocess.run(
            ["conan", "remote", "add", "osp", "https://osp.jfrog.io/artifactory/api/conan/conan-local", "--force"],
            check=True,
        )
        subprocess.run(["conan", "profile", "detect", "--force"], check=True)

        for frame_info in inspect.stack():
            frame = frame_info.frame
            module = inspect.getmodule(frame)
            if module and module.__name__.startswith("hatchling.build") and "config_settings" in frame.f_locals:
                config_settings = frame.f_locals["config_settings"] or {}

        package_list = config_settings.get("CONAN_BUILD")
        if package_list:
            build_packages = " ".join([f"-b {p}/*" for p in package_list.split(",")])
        else:
            build_packages = ""

        install_cmd_str = (
            f"conan install . -u -b missing {build_packages} -of build --format json --out-file graph.json"
        )

        install_args = shlex.split(install_cmd_str)
        result = subprocess.run(install_args)
        assert result.returncode == 0, "Conan install failed"

        if "CONAN_UPLOAD_OSP" in os.environ:
            print("Uploading packages..")
            with open("pkglist.json", "w") as pkglist_file:
                subprocess.run(
                    ["conan", "list", "--graph=graph.json", "--format=json"], check=True, stdout=pkglist_file
                )
            subprocess.run(["conan", "upload", "--confirm", "--list=pkglist.json", "--remote", "osp"], check=True)

        if system_os == "Linux":
            for libfile in glob.glob("build/libcosimc/*"):
                subprocess.run(["patchelf", "--set-rpath", "$ORIGIN", libfile], check=True)
