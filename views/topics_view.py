from rich.table import Table
from rich import box


class TopicsView:
    def __init__(self, ui):
        self.ui = ui

    def show(self, topics: list[tuple[str, str, str | None]]) -> None:
        table = Table(title="Sujets disponibles", box=box.SIMPLE_HEAVY)
        table.add_column("Topic", style="cyan", no_wrap=True)
        table.add_column("Cheat Sheet", overflow="fold")
        table.add_column("Exercices", overflow="fold")
        for slug, cheat, ex_dir in topics:
            table.add_row(slug, cheat, ex_dir or "-")
        self.ui.console.print(table)
