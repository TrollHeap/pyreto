from pathlib import Path
from rich.panel import Panel


class CourseView:
    def __init__(self, ui):
        self.ui = ui

    def show_created(self, cheat: Path, ex_dir: Path | None) -> None:
        self.ui.console.print(Panel.fit(
            f"[bold]Cheat sheet:[/bold] {cheat}\n"
            f"[bold]Exercices:[/bold] {ex_dir if ex_dir else '-'}\n",
            title="🎯 Cours complet généré", border_style="green"))
