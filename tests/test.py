#!/usr/bin/python3

import inspect
import os
import subprocess
import time
import plac
import re
import sys

import tomlkit

def r(*path):
    """
    Takes a relative path from the directory of this python file and returns the absolute path.
    """
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *path)

def run_in_dir(directory, callable):
    cwd = os.getcwd()
    os.chdir(directory)
    result = callable()
    os.chdir(cwd)
    return result

sys.path.append(r("../"))

from build_website import TomlDict


def test_count():
    website_source_dir = r("../website_source")
    counts = TomlDict({})

    for dirpath, dirnames, filenames in os.walk(website_source_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            _, extension = os.path.splitext(filepath)
            if extension in [".py", ".html", ".scss", ".js", ".md", ".conf", ".env", ".json"]:
                with open(filepath, "r") as file:
                    content = file.read()
                while True:
                    match = re.search(r"\(MYTAKTLAUSVEV_VARIABLE\((.+?)\)\)", content)
                    if match is None:
                        break
                    variable = match.group(1)
                    if variable in counts:
                        counts[variable] += 1
                    else:
                        counts[variable] = 1
                    # print("Counted", variable, counts[variable], "time(s)")
                    content = content[match.end():]

    with open(r("counts.toml"), "w") as file:
        tomlkit.dump(counts.get_tomlkit_document(), file)
    
    return counts


def test_readme(counts):
    with open(r("../README.md"), "r") as file:
        readme = file.read()
    match = re.search(r"### Full config variable reference", readme)
    if match is None:
        raise Exception("Config variable reference not found")
    readme = readme[match.end():]
    while True:
        match = re.search(r"\|\s*?`(.+?)`\s*?\|", readme)
        if match is None:
            break
        variable = match.group(1)
        assert variable in counts, f"{variable} is not used"
        assert counts[variable] != "used", f"{variable} is documented twice"
        counts[variable] = "used"
        readme = readme[match.end():]
    
    for variable in counts:
        assert counts[variable] == "used", f"{variable} is not documented"


@plac.flg("only_count", abbrev="c")
def test(only_count=False):
    try:
        counts = test_count()
        if only_count:
            return
        test_readme(counts)
        print("✅ Test passed")
    except AssertionError as exception:
        print(exception)
        print("❌ Test failed")


if __name__ == "__main__":
    plac.call(test)
