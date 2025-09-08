from textual.app import ComposeResult
from textual.widgets import Static 
from textual.containers import Vertical 

class SettingsView(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("⚙️ Settings", id="set-title")
