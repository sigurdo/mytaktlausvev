#!/usr/bin/python3

import os
import subprocess
import shutil
import argparse
import tomlkit
import re
import plac


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
                    (type(sub_dict[key_part]) == tomlkit.items.Table)
                ):
                    sub_dict[key_part] = tomlkit.table()
                sub_dict = sub_dict[key_part]
    
    def update(self, other_toml_dict):
        def recurse(raw_dict, other_raw_dict):
            for key in other_raw_dict:
                tomlkit_table_types = [tomlkit.items.Table, tomlkit.container.OutOfOrderTableProxy]
                if (
                    (key in raw_dict) and
                    (type(raw_dict[key]) in tomlkit_table_types) and
                    (type(other_raw_dict[key]) in tomlkit_table_types)
                ):
                    recurse(raw_dict[key], other_raw_dict[key])
                else:
                    raw_dict[key] = other_raw_dict[key]
        recurse(self.raw_dict, other_toml_dict.raw_dict)
    
    def get_tomlkit_document(self):
        return self.raw_dict


@plac.flg("clean")
@plac.opt("base_config_file", abbrev="b")
@plac.pos("extra_config_files", type=lambda files: files.split(","), help="Comma separated extra config files, e.g. config1.toml,config2.toml")
def build_website(clean=False, base_config_file="config.toml", extra_config_files=[]):
    """
    Config options from `base_config_file` and `extra_config_files` will be merged, the later entries of `extra_config_files` taking higher priority and `base_config_file` taking the lowest priority.
    """

    config_files = [base_config_file, *extra_config_files]

    os.chdir(os.path.dirname(__file__))

    if clean:
        subprocess.call("rm -rf website_build", shell=True)

    shutil.copytree("website_source", "website_build", dirs_exist_ok=True)

    shutil.copytree("static_files", "website_build/site/static", dirs_exist_ok=True)

    config = TomlDict({})
    for config_file in config_files:
        with open(config_file, "r") as file:
            config.update(TomlDict(tomlkit.load(file)))

    for dirpath, dirnames, filenames in os.walk("website_build"):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            _, extension = os.path.splitext(filepath)
            if extension in [".py", ".html", ".scss", ".js", ".md"]:
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
    plac.call(build_website)
