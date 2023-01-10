#!/usr/bin/python3

import argparse
import inspect
import os
import subprocess
import time
import plac

from create_config import create_config
from build_website import build_website
from prompt_utils import create_prompt_session


def wizard():
    prompt_session = create_prompt_session()
    print("Hei, eg er mytaktlausvev-trollmannen.")
    print("Eg hjelper deg med å konfigurere ein studentorchestervev basert på taktlausveven.")
    config_file_path = create_config(prompt_session)
    build_website(extra_config_files=[config_file_path])
    print("Set du opp ein ekte produksjons-tjenar (prod) eller ein lokal utviklingsversjon (dev)?")
    production = prompt_session.prompt_choices(["prod", "dev"]).lower() == "prod"
    if production:
        subprocess.call("./website_build/scripts/reset_production_with_initial_data.sh", shell=True)
    else:
        subprocess.call("./website_build/scripts/reset_with_initial_data.sh", shell=True)
    print("Oppsett er ferdig.")
    domain = "<domenet ditt>" if production else "localhost:8000"
    print(f"Når du har starta opp tjenaren kan du opne http://{domain}/wiki/kom-i-gang/ i nettlesaren din.")
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
