#!/usr/bin/python3

import inspect
import os
import subprocess
import time
import plac
import re


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


def prod_start(log_file_path):
    if prod_is_running():
        print("Production server is already running")
        return
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
    command = f"screen -dmS mytaktlausvev_prod -L -Logfile {log_file_path} docker-compose -f website_build/docker-compose.prod.yaml up --build --force-recreate"
    print(">", command)
    subprocess.run(command, shell=True)


def prod_stop():
    process_id = prod_get_process_id()
    if process_id is None:
        print("Production server is not running")
    subprocess.run(f"kill {process_id}", shell=True)
    if prod_is_running():
        print("Production server was not stopped")
    else:
        print("Production server was stopped")


def prod(operation):
    """
    This is a script that can be used to manage a running production server.
    """
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    log_file_path = "prod_log.txt"
    if operation == "status":
        if prod_is_running():
            print("Production server is running")
        else:
            print("Production server is not running")
        return
    if operation == "start":
        prod_start(log_file_path)
        return
    if operation == "stop":
        prod_stop()
        return
    # if operation == "attach":
    #     subprocess.run("screen -R mytaktlausvev_prod", shell=True)
    if operation == "show-log":
        subprocess.run(f"tail -n 64 {log_file_path}", shell=True)



if __name__ == "__main__":
    plac.call(prod)
