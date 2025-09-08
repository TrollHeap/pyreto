from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static, Button, TextArea 
from textual.containers import Horizontal, Container

class CodeEditor(Container):
    def compose(self) -> ComposeResult:
        yield Static("Editor", id="title")
        yield TextArea.code_editor(id="editor")
        with Horizontal(id="toolbar"):
            yield Button("Run (F5)", variant="primary")
            yield Button("Submit", variant="success")
