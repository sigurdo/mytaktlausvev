#!/usr/bin/python3

import os
import subprocess
import shutil
import argparse
import toml
import re


class TomlDict:
    def __init__(self, toml_dict):
        self.toml_dict = toml_dict
    
    def __getitem__(self, key):
        result = self.toml_dict
        for key_part in key.split("."):
            result = result[key_part]
        return result


def build_website(clean=False, config_file="config.toml"):
    os.chdir(os.path.dirname(__file__))

    if clean:
        subprocess.call("rm -rf website_build", shell=True)

    shutil.copytree("website_source", "website_build", dirs_exist_ok=True)

    shutil.copytree("static_files", "website_build/site/static", dirs_exist_ok=True)

    with open(config_file, "r") as file:
        config = TomlDict(toml.load(file))
    
    for dirpath, dirnames, filenames in os.walk("website_build"):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            _, extension = os.path.splitext(filepath)
            if extension in [".py", ".html", ".scss", ".js"]:
                with open(filepath, "r") as file:
                    build = file.read()
                while True:
                    match = re.search(r"\(MYTAKTLAUSVEV_VARIABLE\((.+?)\)\)", build)
                    if match is None:
                        break
                    variable = match.group(1)
                    print(filepath, end=":\n")
                    print("Replacing", variable, "with", config[variable])
                    build = build[:match.start()] + config[variable] + build[match.end():]
                with open(filepath, "w") as file:
                    file.write(build)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--clean", action="store_true")
    argument_parser.add_argument("--config-file", "-f", required=False)
    arguments = argument_parser.parse_args()
    kwargs = {}
    kwargs["clean"] = arguments.clean
    if arguments.config_file:
        kwargs["config_file"] = arguments.config_file
    build_website(**kwargs)
