#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.text import Text

from menu import MenuChoice, parse_menu_choice
from views.ui import RichUI
from views.course_view import CourseView
from views.topics_view import TopicsView
from views.schedule_view import ScheduleView
from controllers.course_controller import CourseController
from controllers.topics_controller import TopicsController
from controllers.schedule_controller import ScheduleController

from services.openai_factory import build_openai_client
from services.cheatsheet_service import generate_cheatsheet
from services.exercises_service import generate_exercises
from utils.helpers import safe_slug  # pour afficher/normaliser le topic

PATH_DIR = "Developer/exercise/pyreto"  # ajuste si besoin


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


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Pareto Learning (refactor MVC-S)")
    ap.add_argument("topic", nargs="?", help="Sujet à apprendre (ex: awk)")
    ap.add_argument("-n", "--num-ex", type=int, default=5, help="Nombre d'exercices (défaut: 5)")
    ap.add_argument("-b", "--base-dir", type=Path, default=Path.home() / PATH_DIR,
                    help="Répertoire racine des sujets")
    ap.add_argument("--non-interactif", action="store_true",
                    help="Mode non interactif : génère le cours pour <topic> et quitte")
    return ap.parse_args()


def _ask_topic(ui: RichUI, state: AppState, prompt: str = "Sujet (slug)") -> str:
    default = state.last_topic or (state.recent_topics[0] if state.recent_topics else "memory")
    topic = ui.ask_text(f"{prompt} ({default})", default).strip()
    if topic:
        state.remember_topic(topic)
    return topic


def _header(ui: RichUI, state: AppState) -> None:
    recent = ", ".join(state.recent_topics[:3]) or "-"
    cur = state.last_topic or "-"
    ui.console.rule(Text(f"Menu — topic courant: {cur}  |  récents: {recent}", style="cyan"))


def run_interactive(ui: RichUI, state: AppState) -> int:
    """
    Boucle interactive avec handlers complets pour 1/2/3 et préviews.
    Raccourcis: g=cheat, x=exos, r=répéter dernière action, t=changer topic, ?=aide.
    """
    shortcuts = {"g": MenuChoice.CHEATSHEET, "x": MenuChoice.EXERCISES}
    while True:
        _header(ui, state)
        raw = ui.show_menu().strip()
        if raw in shortcuts:
            choice = shortcuts[raw]
        elif raw == "r" and state.last_action:
            # replique la dernière action sur last_topic
            choice = {
                "course": MenuChoice.COURSE,
                "cheat": MenuChoice.CHEATSHEET,
                "ex": MenuChoice.EXERCISES,
            }.get(state.last_action, MenuChoice.QUIT)
        elif raw == "t":
            _ask_topic(ui, state, "Nouveau sujet (slug)")
            continue
        elif raw == "?":
            ui.console.print("[bold]Raccourcis:[/bold] g=cheat, x=exos, r=répéter, t=changer sujet, q=quitter")
            continue
        elif raw == "q":
            choice = MenuChoice.QUIT
        else:
            choice = parse_menu_choice(raw)

        if choice is MenuChoice.QUIT:
            ui.console.print("[bold]Au revoir! 👋[/bold]")
            return 0

        # Handlers
        if choice is MenuChoice.COURSE:
            topic = _ask_topic(ui, state)
            if not topic:
                ui.console.print("[red]Sujet vide — annulé.[/red]")
                continue
            controller = CourseController(ui, CourseView(ui), client=state.client)
            controller.run(state.base, topic)
            state.last_action = "course"

        elif choice is MenuChoice.CHEATSHEET:
            topic = _ask_topic(ui, state)
            if not topic:
                ui.console.print("[red]Sujet vide — annulé.[/red]")
                continue
            with ui.spinner("Génération cheat sheet…"):
                path = generate_cheatsheet(state.base, topic, client=state.client)
            ui.console.print(f"[green]Cheat sheet:[/green] {path}")
            ui.preview_markdown(path, limit_chars=1800)
            if ui.ask_confirm("Ouvrir dans l'éditeur ?", True):
                # utilitaire minimal, ou EditorLauncher si tu l’as
                import os
                import subprocess
                subprocess.run([os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi", str(path)])
            state.last_action = "cheat"

        elif choice is MenuChoice.EXERCISES:
            topic = _ask_topic(ui, state)
            if not topic:
                ui.console.print("[red]Sujet vide — annulé.[/red]")
                continue
            n = ui.ask_int("Combien d'exercices ?", 5, minimum=1, maximum=50)
            with ui.spinner("Génération exercices…"):
                files, launcher = generate_exercises(state.base, topic, n=n, client=state.client)
            count = len(files)
            ui.console.print(f"[green]{count} fichier(s) créé(s)[/green] dans {files[0].parent if files else '(aucun)'}")
            if launcher:
                ui.console.print(f" Lanceur: {launcher}")
            # Choix d’un exercice à ouvrir
            if files and ui.ask_confirm("Prévisualiser un exercice ?", True):
                pick = ui.pick_exercise(files)
                if pick:
                    import os
                    import subprocess
                    subprocess.run([os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi", str(pick)])
            state.last_action = "ex"

        elif choice is MenuChoice.TOPICS:
            TopicsController(ui, TopicsView(ui)).run(state.base)

        elif choice is MenuChoice.SCHEDULE:
            topic = _ask_topic(ui, state)
            if not topic:
                ui.console.print("[red]Sujet vide — annulé.[/red]")
                continue
            ex_dir = state.base / "exercises" / safe_slug(topic)
            ScheduleController(ui, ScheduleView(ui)).run(ex_dir, topic)

        elif choice is MenuChoice.PRACTICE:
            ui.console.print("[yellow]Mode pratique : handler à implémenter (prochaine étape).[/yellow]")

        else:
            ui.console.print("[yellow]Choix non pris en charge.[/yellow]")


def run_non_interactive(ui: RichUI, state: AppState, topic: str, num_ex: int) -> int:
    # équivalent “cours complet” non interactif
    from services.course_service import generate_course
    if not topic.strip():
        ui.console.print("[red]Topic manquant en mode non interactif.[/red]")
        return 2
    with ui.spinner("Génération du cours…"):
        result = generate_course(state.base, topic, client=state.client)
    CourseView(ui).show_created(result["cheatsheet"], result["ex_dir"], result.get("manifest"))
    return 0


def main() -> int:
    args = parse_args()
    ui = RichUI(Console())
    client = build_openai_client(ui)  # Optional

    state = AppState(base=args.base_dir, client=client)

    if args.non_interactif:
        if not args.topic:
            ui.console.print("[red]--non-interactif exige un <topic>.[/red]")
            return 2
        return run_non_interactive(ui, state, args.topic, args.num_ex)

    return run_interactive(ui, state)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        Console().print("\n[red]Interrompu.[/red]")
        raise
