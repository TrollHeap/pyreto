from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from rich.text import Text
from views.rich_ui import RichUI

PATH_DIR = "Developer/exercise/pyreto"


@dataclass
class AppState:
    base: Path
    client: object | None = None
    last_topic: str | None = None
    recent_topics: list[str] = field(default_factory=list)
    last_action: str | None = None  # "course" | "cheat" | "ex"

    def remember_topic(self, topic: str) -> None:
        topic = topic.strip()
        if not topic:
            return
        self.last_topic = topic
        if topic in self.recent_topics:
            self.recent_topics.remove(topic)
        self.recent_topics.insert(0, topic)
        del self.recent_topics[5:]


def header(ui: RichUI, state: AppState) -> None:
    recent = ", ".join(state.recent_topics[:3]) or "-"
    cur = state.last_topic or "-"
    ui.console.rule(Text(f"Menu — topic: {cur} | récents: {recent}", style="cyan"))


def ask_topic(ui: RichUI, state: AppState, prompt: str = "Sujet (slug)") -> str:
    default = state.last_topic or (state.recent_topics[0] if state.recent_topics else "memory")
    topic = ui.ask_text(f"{prompt} ({default})", default).strip()
    if topic:
        state.remember_topic(topic)
    return topic
