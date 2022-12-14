#!/usr/bin/python3

import argparse
import inspect
import os
import subprocess
import time
import tomlkit
import plac

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.lexers import Lexer

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from build_website import TomlDict
from prompt_utils import create_prompt_session


class StaticFilePathValidator(Validator):
    def validate(self, document):
        text = document.text
        static_files_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static_files"))
        file_path = os.path.join(static_files_dir_path, text)
        if not os.path.isfile(file_path):
            raise ValidationError(message=f"Dette må vere filstien til ein fil i {static_files_dir_path}, relativt til static_files-mappa")


class StaticFilePathCompleter(Completer):
    def get_completions(self, document, complete_event):
        word_before_cursor = document.text_before_cursor.lower()
        static_files_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static_files"))
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

class HighLevelConfigEntry:
    def __init__(
        self,
        description,
        config_options_callback,
        validator=None,
        default="",
        completer=None,
        lexer=None,
    ):
        self.description = description
        self.config_options_callback = config_options_callback
        self.validator = validator
        self.default = default
        self.completer = completer
        self.lexer = lexer


high_level_config_entries = [
    HighLevelConfigEntry(
        "Navn på orchester",
        lambda orchestra_name: {
            "appearance.base_page_title": orchestra_name,
            "appearance.navbar.title": orchestra_name,
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
        },
        validator=StaticFilePathValidator(),
        completer=StaticFilePathCompleter(),
    ),
]


def create_config(prompt_session: PromptSession):
    toml_dict = TomlDict({})
    for entry in high_level_config_entries:
        value = prompt_session.prompt(
            f"{entry.description}: ",
            auto_suggest=AutoSuggestFromHistory(),
            validator=entry.validator,
            completer=entry.completer,
            lexer=entry.lexer,
            default=entry.default,
        )

        config_options = entry.config_options_callback(value)

        for option in config_options:
            toml_dict[option] = config_options[option]

    output_file_path = prompt_session.prompt("Lagre konfigurasjon som: ", default="config.toml")
    output_file_is_default = os.path.abspath(output_file_path) == os.path.abspath("config.toml")

    if output_file_is_default:
        with open("config.toml", "r") as file:
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
