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
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from build_website import TomlDict
from prompt_utils import create_prompt_session, choice_validator, ChoiceCompleter, FilePathCompleter


class HighLevelConfigEntry:
    def __init__(
        self,
        description,
        get_config_options,
        help_text=None,
        alternatives=None,
        validator=None,
        default="",
        completer=None,
        lexer=None,
        only_if=None,
    ):
        self.description = description
        self.get_config_options = get_config_options
        self.help_text = help_text
        self.validator = validator
        self.default = default
        self.completer = completer
        self.lexer = lexer
        self.only_if = only_if

        if alternatives is not None:
            self.validator = self.validator or choice_validator(alternatives)
            self.completer = self.completer or ChoiceCompleter(alternatives)


def create_config(prompt_session: PromptSession, high_level_config_entries: list, store_as_default: str):
    toml_dict = TomlDict({})
    for entry in high_level_config_entries:
        if entry.only_if and not entry.only_if(toml_dict):
            continue

        if entry.help_text is not None:
            print(entry.help_text)

        value = prompt_session.prompt(
            f"{entry.description}: ",
            validator=entry.validator,
            completer=entry.completer,
            lexer=entry.lexer,
            default=entry.default,
        )

        config_options = entry.get_config_options(value)

        for option in config_options:
            toml_dict[option] = config_options[option]

    output_file_path = prompt_session.prompt("Lagre konfigurasjon som: ", default=store_as_default, completer=FilePathCompleter())

    if os.path.exists(output_file_path):
        with open(output_file_path, "r") as file:
            previous_config = TomlDict(tomlkit.load(file))
            previous_config.update(toml_dict)
            toml_dict = previous_config

    with open(output_file_path, "w") as file:
        tomlkit.dump(toml_dict.get_tomlkit_document(), file)

    return output_file_path
