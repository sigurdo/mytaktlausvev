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


def build_website(config_files, clean=False):
    website_source_dir = os.path.join(os.path.dirname(__file__), "website_source")
    website_build_dir = os.path.join(os.path.dirname(__file__), "website_build")
    static_files_dir = os.path.join(os.path.dirname(__file__), "static_files")

    if clean:
        if os.path.exists(website_build_dir):
            shutil.rmtree(website_build_dir)

    shutil.copytree(website_source_dir, website_build_dir, dirs_exist_ok=True)

    shutil.copytree(static_files_dir, os.path.join(website_build_dir, "site/static"), dirs_exist_ok=True)

    config = TomlDict({})
    for config_file in config_files:
        with open(config_file, "r") as file:
            config.update(TomlDict(tomlkit.load(file)))
    

    for dirpath, dirnames, filenames in os.walk(website_build_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            _, extension = os.path.splitext(filepath)
            if extension in [".py", ".html", ".scss", ".js", ".md", ".conf", ".env"]:
                with open(filepath, "r") as file:
                    build = file.read()
                while True:
                    match = re.search(r"\(MYTAKTLAUSVEV_VARIABLE\((.+?)\)\)", build)
                    if match is None:
                        break
                    variable = match.group(1)
                    print("Replacing", variable, "with", config[variable])
                    build = build[:match.start()] + config[variable] + build[match.end():]
                with open(filepath, "w") as file:
                    file.write(build)


@plac.pos("main_config_file")
@plac.opt("base_config_file", abbrev="b")
@plac.opt("server_secrets_file", abbrev="s")
@plac.flg("clean")
def build_website_cli(
    main_config_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.toml"),
    base_config_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "taktlausconfig.toml"),
    server_secrets_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "server_secrets.toml"),
    clean=False,
):
    """
    Config options will be merged, `base_config_file` takes the lowest priority and `server_secrets_file` takes the highest priority. `base_config_file` and `server_secrets_file` will be ignored if they don't exist.

    Examples usage:
    Normal:
    ./build_website.py

    Use custom config file:
    ./build_website.py taktfullconfig.toml

    Use custom secrets file:
    ./build_website.py -s taktfullsecrets.toml

    Use custom secrets and config files:
    ./build_website.py -s taktfullsecrets.toml taktfullconfig.toml

    Use custom base config file:
    ./build_website.py -b other_base_config.toml
    """

    config_files = [base_config_file]

    if os.path.exists(main_config_file):
        config_files.append(main_config_file)

    if os.path.exists(server_secrets_file):
        config_files.append(server_secrets_file)

    build_website(config_files, clean=clean)


if __name__ == "__main__":
    plac.call(build_website_cli)
