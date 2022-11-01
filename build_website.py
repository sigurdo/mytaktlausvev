#!/usr/bin/python3

import os
import subprocess
import shutil
import argparse
import toml
import re


def build_website(clean=False):
    os.chdir(os.path.dirname(__file__))

    if clean:
        subprocess.call("rm -rf website_build", shell=True)

    shutil.copytree("website_source", "website_build", dirs_exist_ok=True)

    with open("config.toml", "r") as file:
        config = toml.load(file)
    
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
                    category, variable = match.group(1).split(".")
                    print(filepath, end=":\n")
                    print("Replacing", match.group(1), "with", config[category][variable])
                    build = build[:match.start()] + config[category][variable] + build[match.end():]
                with open(filepath, "w") as file:
                    file.write(build)


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--clean", action="store_true")
    arguments = argument_parser.parse_args()
    build_website(
            clean=arguments.clean
        )
