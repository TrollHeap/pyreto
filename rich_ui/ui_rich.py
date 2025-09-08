#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich import box

from api.openai import OpenAIResponder, OpenAIConfig

class RichUI:
    """Toutes les interactions Rich sont ici. Une seule Console, injectée."""
    def __init__(self, console: Console) -> None:
        self.console = console

    # --- helpers ---

    def spinner(self, desc: str):
        return Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(), transient=True, console=self.console
        )

    def ask_text(self, prompt: str, default: str | None = None) -> str:
        return Prompt.ask(prompt, default=default)

    def ask_int(self, prompt: str, default: int = 1) -> int:
        return IntPrompt.ask(prompt, default=default)

    def ask_confirm(self, prompt: str, default: bool = True) -> bool:
        return Confirm.ask(prompt, default=default)

    # --- OpenAI config (facultatif, mais pratique côté UI) ---

    def ask_openai_client(self) -> Optional[OpenAIResponder]:
        if not self.ask_confirm("Configurer OpenAI maintenant ? (sinon placeholders)", True):
            return None
        model = self.ask_text("Modèle OpenAI", "gpt-5")
        instructions = self.ask_text("Instructions globales", "Tu es concis, précis, et technique.")
        prompt_id = prompt_version = None
        prompt_vars = None
        if self.ask_confirm("Utiliser un prompt réutilisable (dashboard) ?", False):
            prompt_id = self.ask_text("Prompt ID (dashboard)")
            sver = self.ask_text("Prompt version (optionnel)", "")
            prompt_version = sver or None
            vars_str = self.ask_text('Variables JSON (optionnel, ex: {"topic":"awk"})', "")
            import json
            try:
                prompt_vars = json.loads(vars_str) if vars_str else None
            except Exception as e:
                self.console.print(f"[yellow]Variables JSON ignorées:[/yellow] {e}")
        try:
            return OpenAIResponder(OpenAIConfig(
                model=model, instructions=instructions,
                prompt_id=prompt_id, prompt_version=prompt_version, prompt_vars=prompt_vars
            ))
        except Exception as e:
            self.console.print(f"[yellow]Client OpenAI non initialisé:[/yellow] {e}\n"
                               "[yellow]Le script créera des placeholders.[/yellow]")
            return None

    # --- écrans ---

    def show_menu(self) -> str:
        self.console.print(Panel.fit(
            """[bold]🎓 SYSTÈME D'APPRENTISSAGE - LOI DE PARETO[/bold]

1) 🚀 Cours complet  2) 📝 Cheat sheet  3) 💪 Exercices
4) 📚 Pratiquer       5) 📊 Sujets       6) 📅 Planning
7) ❌ Quitter
""", border_style="cyan", title="Menu"))
        return Prompt.ask("Votre choix (1-7)", choices=[str(i) for i in range(1, 8)], default="7")

    def show_cheatsheet_created(self, path: Path) -> None:
        self.console.print(Panel.fit(f"Cheat sheet créé:\n[bold]{path}[/bold]", title="✅ OK"))

    def show_exercises_created(self, paths: list[Path], launcher: Optional[Path]) -> None:
        table = Table(title="Exercices créés", box=box.SIMPLE)
        table.add_column("Fichier", style="cyan")
        for p in paths: table.add_row(str(p))
        self.console.print(table)
        if launcher:
            self.console.print(f"[green]Lanceur:[/green] {launcher}")

    def show_course_summary(self, cheat: Path, ex_dir: Optional[Path], manifest: Path) -> None:
        self.console.print(Panel.fit(
            f"[bold]Cheat sheet:[/bold] {cheat}\n"
            f"[bold]Exercices:[/bold] {ex_dir}\n"
            f"[bold]Manifest:[/bold] {manifest}",
            title="🎯 Cours complet généré", border_style="green"))

    def show_topics(self, topics: list[tuple[str, Path, Optional[Path]]]) -> None:
        table = Table(title="Sujets disponibles", box=box.SIMPLE_HEAVY)
        table.add_column("Topic", style="cyan", no_wrap=True)
        table.add_column("Cheat Sheet", overflow="fold")
        table.add_column("Exercices", overflow="fold")
        for slug, cheat, ex_dir in topics:
            table.add_row(slug, str(cheat), str(ex_dir) if ex_dir else "-")
        self.console.print(table)

    def show_schedule(self, schedule: list[tuple[str, list[str]]], slug: str) -> None:
        if not schedule:
            self.console.print("[yellow]Aucun planning détecté (pas d'exercices datés).[/yellow]")
            return
        table = Table(title=f"Planning (approx.) pour '{slug}'", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("Date", style="green"); table.add_column("Exercices")
        for day, names in schedule:
            table.add_row(day, ", ".join(names))
        self.console.print(table)

    def preview_markdown(self, path: Path, limit_chars: int = 2000) -> None:
        self.console.print(Markdown(path.read_text(encoding="utf-8")[:limit_chars]))

    def pick_exercise(self, files: list[Path]) -> Optional[Path]:
        if not files:
            self.console.print("[red]Aucun fichier d'exercice.[/red]")
            return None
        self.console.print("\n[bold]Exercices disponibles:[/bold]")
        for i, f in enumerate(files, 1):
            self.console.print(f"  {i:02d}. {f.name}")
        idx = IntPrompt.ask("\nChoisissez un exercice (numéro)", default=1)
        idx = max(1, min(idx, len(files)))
        return files[idx - 1]

    def open_in_editor(self, path: Path) -> None:
        import os, subprocess
        subprocess.run([os.environ.get("EDITOR", "vi"), str(path)])
