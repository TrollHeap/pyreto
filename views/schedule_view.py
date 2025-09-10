from rich.table import Table
from rich import box


class ScheduleView:
    def __init__(self, ui):
        self.ui = ui

    def show(self, schedule: list[tuple[str, list[str]]], slug: str) -> None:
        if not schedule:
            self.ui.console.print("[yellow]Aucun planning détecté (pas d'exercices datés).[/yellow]")
            return
        table = Table(title=f"Planning (approx.) pour '{slug}'", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("Date", style="green")
        table.add_column("Exercices")
        for day, names in schedule:
            table.add_row(day, ", ".join(names))
        self.ui.console.print(table)
