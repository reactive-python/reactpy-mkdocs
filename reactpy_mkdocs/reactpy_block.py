from pathlib import Path
from io import StringIO
from traceback import format_exc
from logging import getLogger
from typing import Any, Callable
from urllib.parse import parse_qs

import reactpy
from reactpy import component, use_location, html, use_state
from reactpy.types import ComponentType

log = getLogger(__name__)

REACTPY_RUN = reactpy.run


@component
def reactpy_frame() -> Any:
    location = use_location()

    if not location.search:
        log.error("No files specified in query string")
        return None

    query = parse_qs(location.search.lstrip("?"))
    if "file" not in query or not query["file"]:
        log.error("No file specified in query string")
        return None

    if len(query["file"]) > 1:
        log.error("Multiple files specified in query string")
        return None

    return load_file_view(query["file"][0])


def load_file_view(file: str) -> ComponentType:
    file = Path(file)

    if not file.exists():
        raise FileNotFoundError(str(file.resolve()))

    print_buffer = _PrintBuffer()

    def capture_print(*args, **kwargs):
        buffer = StringIO()
        print(*args, file=buffer, **kwargs)
        print_buffer.write(buffer.getvalue())

    captured_component_constructor = None

    def capture_component(component_constructor):
        nonlocal captured_component_constructor
        captured_component_constructor = component_constructor

    reactpy.run = capture_component
    try:
        code = compile(file.read_text(), str(file), "exec")
        exec(
            code,
            {
                "print": capture_print,
                "__file__": str(file),
                "__name__": file.stem,
            },
        )
    except Exception:
        return _make_error_display(format_exc())
    finally:
        reactpy.run = REACTPY_RUN

    if captured_component_constructor is None:
        return _make_example_did_not_run(str(file))

    @component
    def wrapper():
        return html.div(captured_component_constructor(), print_view())

    @component
    def print_view():
        text, set_text = use_state(print_buffer.getvalue())
        print_buffer.set_callback(set_text)
        return html.pre({"class_name": "printout"}, text) if text else html.div()

    return wrapper()


def _make_error_display(error: str) -> ComponentType:
    @component
    def error_display():
        return html.pre(error)

    return error_display()


def _make_example_did_not_run(file: str):
    @component
    def did_not_run():
        return html.code(f"reactpy.run was never called in {file}")

    return did_not_run()


class _PrintBuffer:
    def __init__(self, max_lines: int = 10):
        self._callback = None
        self._lines = ()
        self._max_lines = max_lines

    def set_callback(self, function: Callable[[str], None]) -> None:
        self._callback = function
        return None

    def getvalue(self) -> str:
        return "".join(self._lines)

    def write(self, text: str) -> None:
        if len(self._lines) == self._max_lines:
            self._lines = self._lines[1:] + (text,)
        else:
            self._lines += (text,)
        if self._callback is not None:
            self._callback(self.getvalue())
