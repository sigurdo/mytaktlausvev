#!/usr/bin/python3

import argparse
import inspect
import os
import subprocess
import time
import tomlkit
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from build_website import TomlDict
from prompt_utils import create_prompt_session

class VariableValidator:
    def __init__(self, variable_name, variable_value):
        self.variable_name = variable_name
        self.variable_value = variable_value
    
    def validate(self) -> bool:
        raise Exception(f".validate() not implemented for {self.__class__}")


class StringValidator(VariableValidator):
    def validate(self) -> bool:
        if type(self.variable_value) != str:
            raise Exception(f"{self.variable_name} må vere ein tekststreng")


class StaticFilePathValidator(StringValidator):
    def validate(self) -> bool:
        super().validate()
        static_files_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static_files"))
        if not os.path.exists(os.path.join(static_files_dir_path, self.variable_value)):
            raise Exception(f"{self.variable_name} må vere filstien til ein fil i {static_files_dir_path}, relativt til static_files-mappa")


class HighLevelConfigEntry:
    def __init__(
        self,
        description,
        config_options_callback,
        validator_class=StringValidator,
        default_value=None,
    ):
        self.description = description
        self.config_options_callback = config_options_callback
        self.validator_class  = validator_class
        self.default_value = default_value


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
    ),
    HighLevelConfigEntry(
        "Logo",
        lambda logo_path: {
            "appearance.navbar.logo": logo_path,
        },
        validator_class=StaticFilePathValidator,
        default_value="images/taktlauslogo.svg",
    ),
]


def create_config(prompt_session: PromptSession):
    toml_dict = TomlDict({})
    for entry in high_level_config_entries:
        while True:
            default_value_text = "" if entry.default_value is None else f" (default: {entry.default_value})"
            value = prompt_session.prompt(
                f"{entry.description}{default_value_text}: ",
                auto_suggest=AutoSuggestFromHistory(),
            ) or entry.default_value
            validator = entry.validator_class(entry.description, value)
            try:
                validator.validate()
            except Exception as exception:
                print(f"{value} er ikkje gyldig: {exception}")
                continue
            break

        config_options = entry.config_options_callback(value)

        for option in config_options:
            toml_dict[option] = config_options[option]

    output_file_path = prompt_session.prompt("Lagre konfigurasjon som (default: config.toml): ") or "config.toml"
    output_file_is_default = os.path.abspath(output_file_path) == os.path.abspath("config.toml")

    if output_file_is_default:
        with open("config.toml", "r") as file:
            previous_config = TomlDict(tomlkit.load(file))
            previous_config.update(toml_dict)
            toml_dict = previous_config

    with open(output_file_path, "w") as file:
        tomlkit.dump(toml_dict.get_tomlkit_document(), file)

    config_files_flag = "" if output_file_is_default else f"-f config.toml {output_file_path} "

    # print("Tada! Du kan nå bygge vevsidea, initialisere databasa og starte han opp med følgande kommando:")
    # print(f"./build_website.py {config_files_flag}&& ./website_build/scripts/reset_with_initial_data.sh && ./website_build/scripts/up.sh")
    # print("Deretter kan opne http://localhost:8000/wiki/kom-i-gang/ i nettlesaren din.")
    # print("Logg inn med brukarnavnet vevansvarleg og passordet passord.")

    return output_file_path


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    argument_parser = argparse.ArgumentParser()
    for parameter in list(inspect.signature(create_config).parameters)[1:]:
        argument_parser.add_argument(parameter)
    arguments = argument_parser.parse_args()
    create_config(create_prompt_session(), **vars(arguments))
