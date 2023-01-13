#!/usr/bin/python3

import inspect
import os
import subprocess
import time
import plac
import re

from build_website import build_website, build_website_cli


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


def prod_get_process_id():
    output = subprocess.run("screen -ls", shell=True, stdout=subprocess.PIPE).stdout.decode("UTF-8")
    for line in output.split("\n"):
        match = re.match(r".*?(\d+)\.mytaktlausvev_prod.*", line)
        if match is None:
            continue
        (process_id,) = match.groups()
        return process_id
    return None


def prod_is_running():
    return prod_get_process_id() is not None


def prod_start():
    log_file_path=r("prod_log.txt")
    if prod_is_running():
        print("Production server is already running")
        return
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
    subprocess.run(f"screen -dmS mytaktlausvev_prod -L -Logfile {log_file_path} docker-compose -f website_build/docker-compose.prod.yaml up --build --force-recreate", shell=True)
    print("Production server was started")


def prod_stop():
    process_id = prod_get_process_id()
    if process_id is None:
        print("Production server is not running")
    subprocess.run(f"kill {process_id}", shell=True)
    if prod_is_running():
        print("Production server was not stopped")
    else:
        print("Production server was stopped")


def prod_rebuild():
    build_website_cli()
    run_in_dir(
        r("website_build"),
        lambda: subprocess.run("docker-compose -f docker-compose.prod.yaml build", shell=True),
    )
    if prod_is_running():
        prod_stop()
    prod_start()


def prod(operation):
    """
    This is a script that can be used to manage a running production server.
    """
    # os.chdir(os.path.dirname(os.path.abspath(__file__)))
    log_file_path = r("prod_log.txt")
    if operation == "status":
        if prod_is_running():
            print("Production server is running")
        else:
            print("Production server is not running")
    elif operation == "start":
        prod_start()
    elif operation == "stop":
        prod_stop()
    elif operation == "rebuild":
        prod_rebuild()
    # if operation == "attach":
    #     subprocess.run("screen -R mytaktlausvev_prod", shell=True)
    elif operation == "print-log":
        subprocess.run(f"cat {log_file_path}", shell=True)
    else:
        print("Operation was not recognized")


if __name__ == "__main__":
    plac.call(prod)
