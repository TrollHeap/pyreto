from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
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

    # Menus / écrans génériques
    def show_menu(self) -> str:
        self.console.print(Panel.fit(
            """[bold]🎓 SYSTÈME D'APPRENTISSAGE - LOI DE PARETO[/bold]

1) 🚀 Cours complet  2) 📝 Cheat sheet  3) 💪 Exercices
4) 📚 Pratiquer       5) 📊 Sujets       6) 📅 Planning
7) ❌ Quitter
""", border_style="cyan", title="Menu"))
        return Prompt.ask("Votre choix (1-7)", choices=[str(i) for i in range(1, 8)], default="7")

    def preview_markdown(self, path: Path, limit_chars: int = 2000) -> None:
        self.console.print(Markdown(path.read_text(encoding="utf-8")[:limit_chars]))
