#!/usr/bin/python3

import argparse
import inspect
import io
import os
import subprocess
import time
import tomlkit
import plac
import re

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import validators

from build_website import TomlDict
from prompt_utils import create_prompt_session, choice_validator, ChoiceCompleter



def get_static_files_dir_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "static_files"))


class StaticFilePathValidator(Validator):
    def validate(self, document):
        text = document.text
        static_files_dir_path = get_static_files_dir_path()
        file_path = os.path.join(static_files_dir_path, text)
        if not os.path.isfile(file_path):
            raise ValidationError(message=f"Dette må vere filstien til ein fil i {static_files_dir_path}, relativt til static_files-mappa")


class FilePathCompleter(Completer):
    def get_completions(self, document, complete_event):
        word_before_cursor = document.text_before_cursor.lower()
        dir_path = f"{os.path.dirname(word_before_cursor)}"
        for entry in os.listdir(dir_path or "./"):
            path = os.path.join(dir_path, entry)
            if word_before_cursor in path:
                yield Completion(
                    text=path,
                    start_position=-len(word_before_cursor),
                )


class StaticFilePathCompleter(Completer):
    def get_completions(self, document, complete_event):
        word_before_cursor = document.text_before_cursor.lower()
        static_files_dir_path = get_static_files_dir_path()
        for dirpath, dirnames, filenames in os.walk(static_files_dir_path):
            for filename in filenames:
                filepath = os.path.join(dirpath[len(static_files_dir_path)+1:], filename)
                if word_before_cursor in filepath:
                    yield Completion(
                        text=filepath,
                        start_position=-len(word_before_cursor),
                    )
        return super().get_completions(document, complete_event)


def is_valid_color_code(text):
    return (
        len(text) == 7
        and text[0] == "#"
        and all(
            character in [str(decimal) for decimal in [*range(10), "a", "b", "c", "d", "e", "f"]]
            for character in text[1:]
        )
    )


class ColorCodeValidator(Validator):
    def validate(self, document):
        text = document.text.lower()
        if not is_valid_color_code(text):
            raise ValidationError(message="Dette må vere ei heksadesimal RGB-fargekode på formatet #<raud><grøn><blå>. Du kan til dømes bruke denne fargevelgeren: https://rgbacolorpicker.com/hex-color-picker.")


class ColorCodeLexer(Lexer):
    def lex_document(self, document):
        def get_line(line_number):
            text = document.text.lower()
            display = [("", document.text)]
            if is_valid_color_code(text):
                display += [
                    ("", " ("),
                    (f"bg:{document.text} fg:{document.text}", " "*8),
                    ("", ")"),
                ]
            return display

        return get_line


class DomainValidator(Validator):
    def validate(self, document):
        text = document.text
        if validators.domain(text) is not True:
            raise ValidationError(message="Dette må vere eit domene, til dømes taktlaus.no.")
        if text[:4] == "www.":
            raise ValidationError(message="Du skal legge inn domenet utan www foran. Det skal da funke både med og utan, viss det er sett opp DNS-peikar for begge.")


class HostingSolutionValidator(Validator):
    def validate(self, document):
        text = document.text
        if text not in ["azure", "server"]:
            raise ValidationError(message='Du må skrive anten "azure" eller "server".\nhttps://github.com/sigurdo/mytaktlausvev/blob/main/guides/set_up_custom_student_orchestra_website/2_azure_eller_server.md')


class UsernameValidator(Validator):
    def validate(self, document):
        text = document.text
        if re.fullmatch(r"[a-z]+", text) is None:
            raise ValidationError(message="Brukarnamnet kan berre innehalde små bokstavar fra A til Z.")


class HighLevelConfigEntry:
    def __init__(
        self,
        description,
        config_options_callback,
        help_text=None,
        alternatives=None,
        validator=None,
        default="",
        completer=None,
        lexer=None,
    ):
        self.description = description
        self.config_options_callback = config_options_callback
        self.help_text = help_text
        self.validator = validator
        self.default = default
        self.completer = completer
        self.lexer = lexer

        if alternatives is not None:
            self.validator = self.validator or choice_validator(alternatives)
            self.completer = self.completer or ChoiceCompleter(alternatives)


def convert_to_ico(logo_path):
    static_files_dir_path = get_static_files_dir_path()
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


high_level_config_entries = [
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
        validator=ColorCodeValidator(),
        lexer=ColorCodeLexer(),
    ),
    HighLevelConfigEntry(
        "Logo",
        lambda logo_path: {
            "appearance.navbar.logo": logo_path,
            "appearance.favicon": convert_to_ico(logo_path),
        },
        validator=StaticFilePathValidator(),
        completer=StaticFilePathCompleter(),
    ),
    HighLevelConfigEntry(
        "Domene",
        lambda domain: {
            "initial_data.site.domain": domain,
            "nginx.http_server_name": f"{domain} www.{domain}",
            "nginx.https_server_name": f"{domain} www.{domain}",
        },
        validator=DomainValidator(),
    ),
    HighLevelConfigEntry(
        "Type hosting",
        lambda hosting: {
            "production.hosting_solution": hosting,
        },
        help_text="Du må nå leggje inn kva type hosting du skal bruke.\nForklaring av kva som meinast med det finner du her:\nhttps://github.com/sigurdo/mytaktlausvev/blob/main/guides/set_up_custom_student_orchestra_website/2_azure_eller_server.md.",
        alternatives=["azure", "server"],
    ),
    HighLevelConfigEntry(
        "Brukarnavn",
        lambda username: {
            "initial_data.superuser.username": username,
        },
        help_text="Du må nå leggje inn brukarnavn og passord til den fyrste superbrukaren (administrator).\nInformasjonen vil verte lagra i klartekst, så ikkje bruk eit passord du brukar andre stadar, og endre det så fort du har logga inn.",
        default="vevansvarleg",
        validator=UsernameValidator(),
    ),
    HighLevelConfigEntry(
        "Passord",
        lambda password: {
            "initial_data.superuser.password": password,
        },
        default="password",
    ),
]


def create_config(prompt_session: PromptSession):
    toml_dict = TomlDict({})
    for entry in high_level_config_entries:
        if entry.help_text is not None:
            print(entry.help_text)

        value = prompt_session.prompt(
            f"{entry.description}: ",
            validator=entry.validator,
            completer=entry.completer,
            lexer=entry.lexer,
            default=entry.default,
        )

        config_options = entry.config_options_callback(value)

        for option in config_options:
            toml_dict[option] = config_options[option]

    output_file_path = prompt_session.prompt("Lagre konfigurasjon som: ", default="config.toml", completer=FilePathCompleter())

    if os.path.exists(output_file_path):
        with open(output_file_path, "r") as file:
            previous_config = TomlDict(tomlkit.load(file))
            previous_config.update(toml_dict)
            toml_dict = previous_config

    with open(output_file_path, "w") as file:
        tomlkit.dump(toml_dict.get_tomlkit_document(), file)

    return output_file_path


def create_config_cli():
    prompt_session = create_prompt_session()
    output_file_path = create_config(prompt_session)

    output_file_is_default = os.path.abspath(output_file_path) == os.path.abspath("config.toml")
    config_files_flag = "" if output_file_is_default else f"-f config.toml {output_file_path} "

    print("Tada! Du kan nå bygge vevsidea, initialisere databasa og starte han opp med følgande kommando:")
    print(f"./build_website.py {config_files_flag}&& ./website_build/scripts/reset_with_initial_data.sh && ./website_build/scripts/up.sh")
    print("Deretter kan opne http://localhost:8000/wiki/kom-i-gang/ i nettlesaren din.")
    print("Logg inn med brukarnavnet vevansvarleg og passordet passord.")


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    plac.call(create_config_cli)
