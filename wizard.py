#!/usr/bin/python3

import argparse
import inspect
import os
import subprocess
import time
from create_config import create_config
from build_website import build_website

def wizard():
    print("Hei, eg er mytaktlausvev-trollmannen.")
    print("Eg hjelper deg med å konfigurere ein studentorchestervev basert på taktlausveven.")
    config_file_path = create_config()
    build_website(config_files=["config.toml", config_file_path])
    print("Set du opp ein ekte produksjons-tjenar (prod) eller ein lokal utviklingsversjon (dev)?")
    while True:
        prod_or_dev = input("prod/dev: ").lower()
        if prod_or_dev in ["prod", "dev"]:
            production = prod_or_dev == "prod"
            break
        print('Venlegast skriv anten "prod" eller "dev".')
    if production:
        subprocess.call("./website_build/scripts/reset_production_with_initial_data.sh", shell=True)
    else:
        subprocess.call("./website_build/scripts/reset_with_initial_data.sh", shell=True)
    print("Oppsett er ferdig.")
    domain = "<domenet ditt>" if production else "localhost:8000"
    print(f"Når du har starta opp tjenaren kan du opne http://{domain}/wiki/kom-i-gang/ i nettlesaren din.")
    print('Logg inn med brukernavnet "vevansvarleg" og passordet "passord".')
    print("Vil du starte opp tjenaren nå?")
    while True:
        yes_or_no = input("ja/nei: ").lower()
        if yes_or_no in ["ja", "nei"]:
            start_server = yes_or_no == "ja"
            break
        print('Venlegast skriv anten "ja" eller "nei".')
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
    argument_parser = argparse.ArgumentParser()
    for parameter in inspect.signature(wizard).parameters:
        argument_parser.add_argument(parameter)
    arguments = argument_parser.parse_args()
    wizard(**vars(arguments))
