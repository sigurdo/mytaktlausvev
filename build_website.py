#!/usr/bin/python3

import os
import subprocess
import shutil
import argparse
import toml
import re


class TomlDict:
    def __init__(self, raw_dict):
        self.raw_dict = raw_dict
    
    def __getitem__(self, key):
        result = self.raw_dict
        for key_part in key.split("."):
            result = result[key_part]
        return result
    
    def __setitem__(self, key, value):
        sub_dict = self.raw_dict
        key_split = key.split(".")
        for i, key_part in enumerate(key_split):
            if i == len(key_split) - 1:
                sub_dict[key_part] = value
            else:
                if not (
                    (key_part in sub_dict) and
                    (type(sub_dict[key_part]) == dict)
                ):
                    sub_dict[key_part] = {}
                sub_dict = sub_dict[key_part]
    
    def update(self, other_toml_dict):
        def recurse(raw_dict, other_raw_dict):
            for key in other_raw_dict:
                if (
                    (key in raw_dict) and
                    (type(raw_dict[key]) == dict) and
                    (type(other_raw_dict[key]) == dict)
                ):
                    recurse(raw_dict[key], other_raw_dict[key])
                else:
                    raw_dict[key] = other_raw_dict[key]
        recurse(self.raw_dict, other_toml_dict.raw_dict)


def build_website(clean=False, config_files=["config.toml"]):
    """
    If multiple config files are provided, config options will be merged, the last files in the list taking the highest priority.
    """

    os.chdir(os.path.dirname(__file__))

    if clean:
        subprocess.call("rm -rf website_build", shell=True)

    shutil.copytree("website_source", "website_build", dirs_exist_ok=True)

    shutil.copytree("static_files", "website_build/site/static", dirs_exist_ok=True)

    config = TomlDict({})
    for config_file in config_files:
        with open(config_file, "r") as file:
            config.update(TomlDict(toml.load(file)))
    
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
    os.chdir(os.path.dirname(__file__))
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--clean", action="store_true")
    argument_parser.add_argument("--config-files", "-f", nargs="+", required=False)
    arguments = argument_parser.parse_args()
    kwargs = {}
    kwargs["clean"] = arguments.clean
    if arguments.config_files:
        kwargs["config_files"] = arguments.config_files
    build_website(**kwargs)
