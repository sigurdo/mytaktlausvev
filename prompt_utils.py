from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.named_commands import end_of_line
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator


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
