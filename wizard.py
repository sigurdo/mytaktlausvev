#!/usr/bin/python3

import argparse
import inspect
import os
import subprocess
import time
import plac
import tomlkit

from create_config import create_config
from build_website import build_website
from prompt_utils import create_prompt_session
from build_website import TomlDict


def wizard():
    prompt_session = create_prompt_session()
    print("Hei, eg er mytaktlausvev-trollmannen.")
    print("Eg hjelper deg med å konfigurere ein studentorchestervev basert på taktlausveven.")
    config_file_path = create_config(prompt_session)
    with open(config_file_path, "r") as file:
        config = TomlDict(tomlkit.load(file))
    build_website(extra_config_files=[config_file_path])
    if config["production.hosting_solution"] == "server":
        print("Er dette den serveren du faktisk skal hoste nettsida på?")
        production = prompt_session.prompt_yes_no()
    else:
        production = False
    if production:
        subprocess.call("./website_build/scripts/reset_production_with_initial_data.sh", shell=True)
    else:
        subprocess.call("./website_build/scripts/reset_with_initial_data.sh", shell=True)
    print("Oppsett er ferdig.")
    site_url = f'https://{config["initial_data.site.domain"]}' if production else "http://localhost:8000"
    print(f"Når du har starta opp tjenaren kan du opne {site_url}/wiki/kom-i-gang/ i nettlesaren din.")
    print('Logg inn med brukernavnet "vevansvarleg" og passordet "passord".')
    print("Vil du starte opp tjenaren nå?")
    start_server = prompt_session.prompt_yes_no()
    start_command = (
        "docker-compose -f website_build/docker-compose.prod.yaml up --build --force-recreate"
        if production else
        "./website_build/scripts/up.sh"
    )
    if start_server:
        subprocess.call(start_command, shell=True)
    else:
        print("Den er grei, start tjenaren når du vil med følgande kommando:")
        print(start_command)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    plac.call(wizard)
