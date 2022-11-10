from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.named_commands import end_of_line

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


def create_prompt_session() -> PromptSession:
    prompt_session = PromptSession(
        key_bindings=key_bindings
    )
    return prompt_session
