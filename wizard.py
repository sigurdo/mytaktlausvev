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
from prod import prod_start



prod_env_template = """\
DEBUG=0
PRODUCTION=1
ALLOWED_HOSTS={allowed_hosts}
CSRF_TRUSTED_ORIGINS={csrf_trusted_origins}

CERTBOT_EMAIL={certbot_email}
USE_LOCAL_CA=1

POSTGRES_DB=taktlaus_db
POSTGRES_USER=taktlaus
POSTGRES_PASSWORD=taktlaus
"""


@plac.pos("config_file")
def wizard(config_file=None):
    """
    MyTaktlausvev setup wizard.
    """
    mytaktlausvev_dir = os.path.abspath(os.path.dirname(__file__))
    prompt_session = create_prompt_session()
    print("Hei, eg er mytaktlausvev-trollmannen.")
    print("Eg hjelper deg med å konfigurere ein studentorchestervev basert på taktlausveven.")
    config_file_path = config_file or create_config(prompt_session)
    with open(config_file_path, "r") as file:
        config = TomlDict(tomlkit.load(file))
    if config["production.hosting_solution"] == "server":
        print("Er dette den serveren du faktisk skal hoste nettsida på?")
        production = prompt_session.prompt_yes_no()
    else:
        production = False
    domain = config["initial_data.site.domain"]
    if production:
        prod_env_path = os.path.join(mytaktlausvev_dir, "website_source/deployment/.prod.env")
        if os.path.exists(prod_env_path):
            print("Du har allereie ein .prod.env-fil. Vil du bruke denne? Hvis du svarar nei vert ho overskrivi av ei ny.")
            make_prod_env = not prompt_session.prompt_yes_no()
        else:
            make_prod_env = True
        if make_prod_env:
            print("Certbot trenger ein e-post-addresse å kontakte deg om sikkjerheitsproblem med HTTPS-sertifikatet.")
            certbot_email = prompt_session.prompt("epost-addresse: ")
            prod_env = prod_env_template.format(
                allowed_hosts=f"{domain} www.{domain}",
                csrf_trusted_origins=f"https://{domain} https://www.{domain}",
                certbot_email=certbot_email,
            )
            with open(prod_env_path, "w") as file:
                file.write(prod_env)
    build_website(extra_config_files=[config_file_path])
    if production:
        subprocess.run(os.path.join(mytaktlausvev_dir, "website_build/scripts/reset_production_with_initial_data.sh"))
    else:
        subprocess.run(os.path.join(mytaktlausvev_dir, "website_build/scripts/reset_with_initial_data.sh"))
    print("Oppsett er ferdig.")
    site_url = f'https://{domain}' if production else "http://localhost:8000"
    if production:
        print("Vil du starte opp serveren nå?")
        start_server = prompt_session.prompt_yes_no()
        if start_server:
            prod_start()
            print("Sånn, produksjonsserveren startar no opp i bakgrunnen. Dette kan ta nokre minutt.")
            print("Du kan stoppe serveren med ./prod.py stop")
        else:
            print("Den er grei. Isåfall kan du starte serveren sjøl med følgande kommando:")
            print("./prod.py start")
    else:
        print("Du kan nå starte opp den lokale utviklingsserveren din med følgande kommando:")
        print("./website_build/scripts/up.sh")
    print(f"Når serveren er oppe kan du gå til {site_url}/wiki/kom-i-gang/ i nettlesaren din.")
    print(f'Logg inn med brukernavnet "{config["initial_data.superuser.username"]}" og passordet "{config["initial_data.superuser.password"]}".')


if __name__ == "__main__":
    plac.call(wizard)
