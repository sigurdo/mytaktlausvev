import os
import re

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.named_commands import end_of_line
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

import validators


key_bindings = KeyBindings()
@key_bindings.add("end")
def _(event):
    """
    Insert suggestion when user presses end.
    """
    suggestion = event.current_buffer.suggestion
    if suggestion:
        event.current_buffer.insert_text(suggestion.text)
    end_of_line(event)


class ChoiceCompleter(Completer):
    def __init__(self, choices):
        self.choices = choices
        return super().__init__()

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor.lower()
        for choice in self.choices:
            if text_before_cursor in choice:
                yield Completion(
                    text=choice,
                    start_position=-len(text_before_cursor),
                )


def choice_validator(choices):
    choices_comma_or_separated = (
        (
            f'"{choices[0]}"'
        )
        if len(choices) == 1 else
        (
            '"' + '", "'.join(choices[:-1]) + f'" eller "{choices[-1]}"'
        )
    )
    return Validator.from_callable(
        lambda text: text in choices,
        error_message=f"Venlegast skriv anten {choices_comma_or_separated}",
        move_cursor_to_end=True,
    )


class FilePathCompleter(Completer):
    def __init__(self, start_dir="./", recursive=False):
        self.start_dir = start_dir
        self.recursive = recursive

    def get_completions(self, document, complete_event):
        word_before_cursor = document.text_before_cursor.lower()
        if self.recursive:
            for dirpath, dirnames, filenames in os.walk(self.start_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath[len(self.start_dir)+1:], filename)
                    if word_before_cursor in filepath:
                        yield Completion(
                            text=filepath,
                            start_position=-len(word_before_cursor),
                        )
        else:
            dir_path = f"{os.path.join(self.start_dir, os.path.dirname(word_before_cursor))}"
            for entry in os.listdir(dir_path or self.start_dir):
                path = os.path.join(dir_path, entry)
                if word_before_cursor in path:
                    yield Completion(
                        text=path,
                        start_position=-len(word_before_cursor),
                    )


class FilePathIsFileValidator(Validator):
    def __init__(self, start_dir="./"):
        self.start_dir = start_dir

    def validate(self, document):
        file_path = os.path.join(self.start_dir, document.text)
        if not os.path.isfile(file_path):
            raise ValidationError(message=f"Dette må vere den relative filstien til ein fil i mappa {self.start_dir}.")


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


class EmailValidator(Validator):
    def validate(self, document):
        text = document.text
        if validators.email(text) is not True:
            raise ValidationError(message="Dette må vere ei epost-addresse.")


class UsernameValidator(Validator):
    def validate(self, document):
        text = document.text
        if re.fullmatch(r"[a-z]+", text) is None:
            raise ValidationError(message="Brukarnamnet kan berre innehalde små bokstavar fra A til Z.")


class PromptSessionCustom(PromptSession):
    def prompt(self, *args, **kwargs):
        """
        Override `prompt()` method to reset kwarg values back to previous values at the end.
        """
        previous_kwarg_values = {
            kwarg: getattr(self, kwarg, "don't touch me")
            for kwarg in kwargs
        }
        result = super().prompt(*args, **kwargs)
        for kwarg, value in previous_kwarg_values.items():
            if value != "don't touch me":
                setattr(self, kwarg, value)
        return result


    def prompt_choices(self, choices, message=None, completer=None, validator=None) -> str:
        message = message or ("/".join(choices) + ": ")
        completer = completer or ChoiceCompleter(choices)
        validator = validator or choice_validator(choices)
        return self.prompt(
            message,
            completer=completer,
            validator=validator,
        )

    def prompt_yes_no(self) -> bool:
        return self.prompt_choices(["ja", "nei"]).lower() == "ja"


def create_prompt_session() -> PromptSessionCustom:
    prompt_session = PromptSessionCustom(
        key_bindings=key_bindings,
        color_depth=ColorDepth.TRUE_COLOR,
    )
    return prompt_session
