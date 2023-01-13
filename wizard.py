#!/usr/bin/python3

import argparse
import inspect
import io
import os
import subprocess
import time
import plac
import tomlkit
import random
import string

from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from create_config import create_config, HighLevelConfigEntry
from build_website import build_website
import prompt_utils
from build_website import TomlDict
from prod import prod_start


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


def convert_to_ico(logo_path):
    static_files_dir_path = r("static_files")
    ico_path = f"{os.path.splitext(logo_path)[0]}.ico"
    try:
        with open(os.path.join(static_files_dir_path, logo_path), "rb") as file:
            logo = io.BytesIO(file.read())
        if os.path.splitext(logo_path)[1] == ".svg":
                drawing = svg2rlg(logo)
                logo = io.BytesIO()
                renderPM.drawToFile(drawing, logo, fmt="PNG")
        Image.open(
            logo
        ).save(
            os.path.join(static_files_dir_path, ico_path)
        )
    except Exception as exception:
        print(exception)
        print("Logoen kunne ikkje konverterast automatisk til .ico-fil.")
        print(f"Du må difor konvertere til den til ei .ico-fil på eiga hand og leggje ho inn med filstien {os.path.join(static_files_dir_path, ico_path)}.")
        print("Du kan fullføre trollmannen før du gjer dette.")
    return ico_path


config_entries = [
    HighLevelConfigEntry(
        "Navn på orchester",
        lambda orchestra_name: {
            "appearance.base_page_title": orchestra_name,
            "appearance.navbar.title": orchestra_name,
            "appearance.navbar.title_short": "",
            "initial_data.orchestra_name": orchestra_name,
        },
    ),
    HighLevelConfigEntry(
        "Temafarge",
        lambda theme_color: {
            "appearance.primary_color": theme_color,
            "appearance.navbar.development_background_color": theme_color,
        },
        default="#",
        validator=prompt_utils.ColorCodeValidator(),
        lexer=prompt_utils.ColorCodeLexer(),
    ),
    HighLevelConfigEntry(
        "Logo",
        lambda logo_path: {
            "appearance.navbar.logo": logo_path,
            "appearance.favicon": convert_to_ico(logo_path),
        },
        validator=prompt_utils.FilePathIsFileValidator(start_dir=r("static_files")),
        completer=prompt_utils.FilePathCompleter(start_dir=r("static_files"), recursive=True),
    ),
    HighLevelConfigEntry(
        "Domene",
        lambda domain: {
            "initial_data.site.domain": domain,
            "production.server.nginx.http_server_name": f"{domain} www.{domain}",
            "production.server.nginx.https_server_name": f"{domain} www.{domain}",
            "production.server.environment.allowed_hosts": f"{domain} www.{domain}",
            "production.server.environment.csrf_trusted_origins": f"https://{domain} https://www.{domain}",
        },
        validator=prompt_utils.DomainValidator(),
    ),
]

server_secrets_entries = [
    HighLevelConfigEntry(
        "Type hosting",
        lambda hosting: {
            "production.hosting_solution": hosting,
        },
        help_text="Du må nå leggje inn kva type hosting du skal bruke.\nForklaring av kva som meinast med det finner du her:\nhttps://github.com/sigurdo/mytaktlausvev/blob/main/guides/set_up_custom_student_orchestra_website/2_azure_eller_server.md.",
        alternatives=["azure", "server"],
    ),
    HighLevelConfigEntry(
        "Certbot epost-addresse",
        lambda email: {
            "production.server.environment.certbot_email": email,
            "production.server.environment.database_password": "".join(random.choice(string.ascii_letters + string.digits) for _ in range(32)),
        },
        help_text="Certbot trenger ein epost-addresse for å kontakte deg om eventuelle sikkjerheitsproblem med HTTPS-sertifikatet.",
        validator=prompt_utils.EmailValidator(),
        only_if=lambda config: (
            config["production.hosting_solution"] == "server"
        ),
    ),
    HighLevelConfigEntry(
        "Brukarnavn",
        lambda username: {
            "initial_data.superuser.username": username,
        },
        help_text="Du må nå leggje inn brukarnavn og passord til den fyrste superbrukaren (administrator).\nInformasjonen vil verte lagra i klartekst, så ikkje bruk eit passord du brukar andre stadar, og endre det så fort du har logga inn.",
        default="vevansvarleg",
        validator=prompt_utils.UsernameValidator(),
    ),
    HighLevelConfigEntry(
        "Passord",
        lambda password: {
            "initial_data.superuser.password": password,
        },
        default="password",
    ),
]


@plac.opt("config_file")
@plac.opt("server_secrets_file")
def wizard(config_file=None, server_secrets_file=None):
    """
    MyTaktlausvev setup wizard.

    By providing config and server secrets files, config options will be taken from them instead of from the command line.
    """
    prompt_session = prompt_utils.create_prompt_session()
    print("Hei, eg er mytaktlausvev-trollmannen.")
    print("Eg hjelper deg med å konfigurere ein studentorchestervev basert på taktlausveven.")
    print("Du kan når som helst avbryte meg med Ctrl+C.")
    config_file_path = config_file or create_config(prompt_session, config_entries, "config.toml")
    with open(config_file_path, "r") as file:
        config = TomlDict(tomlkit.load(file))
    server_secrets_file_path = server_secrets_file or create_config(prompt_session, server_secrets_entries, "server_secrets.toml")
    with open(server_secrets_file_path, "r") as file:
        server_secrets = TomlDict(tomlkit.load(file))
    if server_secrets["production.hosting_solution"] == "server":
        print("Er dette den serveren du faktisk skal hoste nettsida på?")
        production = prompt_session.prompt_yes_no()
    else:
        production = False
    domain = config["initial_data.site.domain"]
    if production and os.path.isdir(r("website_build")):
        print("Det finst allereie ei website_build-mappe, som betyr at du har gjort oppsett allereie. Vil du likevel byggje kildekoden på nytt?")
        build = prompt_session.prompt_yes_no()
        print("Vil du resette databasen? Dette vil slette all dataen som er der nå.")
        reset_database = prompt_session.prompt_yes_no()
    else:
        build = True
        reset_database = True
    if build:
        build_website([r("taktlausconfig.toml"), config_file_path, server_secrets_file_path])
    if production:
        def f():
            subprocess.run(f'docker-compose -f docker-compose.prod.yaml down {"-v" if reset_database else ""} --remove-orphans', shell=True)
            subprocess.run("docker-compose -f docker-compose.prod.yaml build", shell=True)
            subprocess.run("docker-compose -f docker-compose.prod.yaml run --rm django python site/manage.py migrate", shell=True)
            if reset_database:
                subprocess.run("docker-compose -f docker-compose.prod.yaml run --rm django site/manage.py mytaktlausvev_create_initial_data", shell=True)
            subprocess.run("docker-compose -f docker-compose.prod.yaml down", shell=True)
        run_in_dir(r("website_build"), f)
    else:
        print("Vi setter nå opp ein lokal utviklingsversjon av vevsida di.")
        print("Vil du ha utviklingsdata i databasen? Dette gjer at sida vil føles mykje mindre tom.")
        dev_data = prompt_session.prompt_yes_no()
        if dev_data:
            subprocess.run(r("website_build/scripts/reset.sh"))
        else:
            subprocess.run(r("website_build/scripts/reset_with_initial_data.sh"))
    print("Oppsett er ferdig.")
    site_url = f'https://{domain}' if production else "http://localhost:8000"
    if production:
        print("Vil du starte opp serveren nå?")
        start_server = prompt_session.prompt_yes_no()
        if start_server:
            prod_start()
            print("Produksjonsserveren startar no opp i bakgrunnen. Dette kan ta nokre minutt.")
            print("Du kan stoppe serveren med ./prod.py stop")
        else:
            print("Den er grei. Isåfall kan du starte serveren sjøl med følgande kommando:")
            print("./prod.py start")
    else:
        print("Du kan nå starte opp den lokale utviklingsserveren din med følgande kommando:")
        print("./website_build/scripts/up.sh")
    print(f"Når serveren er oppe kan du gå til {site_url}/wiki/kom-i-gang/ i nettlesaren din.")
    print(f'Logg inn med brukernavnet "{server_secrets["initial_data.superuser.username"]}" og passordet "{server_secrets["initial_data.superuser.password"]}".')


if __name__ == "__main__":
    plac.call(wizard)
