from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path

from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich import box
from rich.prompt import Prompt
from rich.console import Console
from rich.prompt import IntPrompt, Confirm
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn


class RichUI:
    """Primitives Rich : affichage + input. AUCUN objet métier construit ici."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    @contextmanager
    def spinner(self, desc: str):
        prog = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                        TimeElapsedColumn(), transient=True, console=self.console)
        prog.start()
        prog.add_task(desc, total=None)
        try:
            yield
        finally:
            prog.stop()

    # Inputs
    def ask_text(self, prompt: str, default: str | None = None) -> str:
        return Prompt.ask(prompt, default=default)

    def ask_int(self, prompt: str, default: int = 1, *, minimum=None, maximum=None) -> int:
        while True:
            v = IntPrompt.ask(prompt, default=default)
            if minimum is not None and v < minimum:
                self.console.print(f"[yellow]≥ {minimum}")
                continue
            if maximum is not None and v > maximum:
                self.console.print(f"[yellow]≤ {maximum}")
                continue
            return v

    def ask_confirm(self, prompt: str, default: bool = True) -> bool:
        return Confirm.ask(prompt, default=default)

    def show_menu(self) -> str:
        self.console.clear()

        # --- Header
        title = Text("🎓 SYSTÈME D'APPRENTISSAGE — LOI DE PARETO", style="bold cyan")
        subtitle = Text("Choisis un mode. Astuce: tape un chiffre (1–7) ou 'q' pour quitter.", style="dim")

        # --- Grid (3 colonnes, 2 rangées + ligne quitter)
        grid = Table.grid(padding=(0, 2), expand=False)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="left", ratio=1)

        grid.add_row(
            "[bold]1)[/bold] 🚀 Cours complet",
            "[bold]2)[/bold] 📝 Cheat sheet",
            "[bold]3)[/bold] 💪 Exercices"
        )
        grid.add_row(
            "[bold]4)[/bold] 📚 Pratiquer",
            "[bold]5)[/bold] 📊 Sujets",
            "[bold]6)[/bold] 📅 Planning"
        )

        quit_line = Text("7) ❌ Quitter", style="bold red")

        # --- Conteneur principal
        body = Panel.fit(
            Align.left(grid),
            title="Menu",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        )

        # --- Rendu
        self.console.print(Align.center(title))
        self.console.print(Align.center(subtitle))
        self.console.print(Rule(style="dim"))
        self.console.print(Align.center(body))
        self.console.print(Align.center(quit_line))
        self.console.print(Rule(style="dim"))

        # --- Saisie (avec alias 'q' -> '7')
        choices = [str(i) for i in range(1, 8)] + ["q", "Q"]
        answer = Prompt.ask("Votre choix", choices=choices, default="7")

        if answer.lower() == "q":
            return "7"
        return answer

    def preview_markdown(self, path: Path, limit_chars: int = 2000) -> None:
        self.console.print(Markdown(path.read_text(encoding="utf-8")[:limit_chars]))
