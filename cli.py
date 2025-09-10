#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from pathlib import Path
from rich.console import Console

from menu import MenuChoice, parse_menu_choice
from views.ui import RichUI
from services.openai_factory import build_openai_client
from app_state import AppState, PATH_DIR, header, ask_topic
from handlers import (
    handle_course, handle_cheatsheet, handle_exercises,
    handle_topics, handle_schedule,
)

# ---------------- Args ----------------


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Pareto Learning (MVC-S) — mode interactif")
    ap.add_argument(
        "-b", "--base-dir",
        type=Path,
        default=Path.home() / PATH_DIR,
        help="Répertoire racine des sujets",
    )
    return ap.parse_args()

# ------------- Routing helpers -------------


_SHORTCUTS = {"g": MenuChoice.CHEATSHEET, "x": MenuChoice.EXERCISES}


def resolve_choice(raw: str, last_action: str | None) -> MenuChoice | None:
    """
    Mappe l'entrée utilisateur vers un MenuChoice.
    Retourne None pour les commandes 'meta' gérées en amont (t, ?, entrée vide).
    """
    raw = (raw or "").strip()
    if not raw or raw == "?":
        return None
    if raw in _SHORTCUTS:
        return _SHORTCUTS[raw]
    if raw == "r" and last_action:
        return {
            "course": MenuChoice.COURSE,
            "cheat": MenuChoice.CHEATSHEET,
            "ex": MenuChoice.EXERCISES,
        }.get(last_action, MenuChoice.QUIT)
    if raw == "q":
        return MenuChoice.QUIT
    return parse_menu_choice(raw)


def dispatch_choice(ui: RichUI, state: AppState, choice: MenuChoice) -> bool:
    """
    Exécute l'action associée à 'choice'.
    Retourne True pour continuer la boucle, False pour quitter.
    """
    needs_topic = {
        MenuChoice.COURSE,
        MenuChoice.CHEATSHEET,
        MenuChoice.EXERCISES,
        MenuChoice.SCHEDULE,
    }

    if choice in needs_topic:
        topic = ask_topic(ui, state)
        if not topic:
            ui.console.print("[red]Sujet vide — annulé.[/red]")
            return True

        if choice is MenuChoice.COURSE:
            handle_course(ui, state, topic)
            return True

        if choice is MenuChoice.CHEATSHEET:
            handle_cheatsheet(ui, state, topic)
            return True

        if choice is MenuChoice.EXERCISES:
            n = ui.ask_int("Combien d'exercices ?", 5, minimum=1, maximum=50)
            handle_exercises(ui, state, topic, n)
            return True

        if choice is MenuChoice.SCHEDULE:
            handle_schedule(ui, state, topic)
            return True

    if choice is MenuChoice.TOPICS:
        handle_topics(ui, state)
        return True

    if choice is MenuChoice.PRACTICE:
        ui.console.print("[yellow]Mode pratique : handler à implémenter.[/yellow]")
        return True

    if choice is MenuChoice.QUIT:
        ui.console.print("[bold]Au revoir! 👋[/bold]")
        return False

    ui.console.print("[yellow]Choix non pris en charge.[/yellow]")
    return True

# ------------- Interactive loop -------------


def run_interactive(ui: RichUI, state: AppState) -> int:
    while True:
        header(ui, state)
        raw = ui.show_menu().strip()

        # commandes meta
        if raw == "t":
            ask_topic(ui, state, "Nouveau sujet (slug)")
            continue
        if raw == "?":
            ui.console.print("[bold]Raccourcis:[/bold] g=cheat, x=exos, r=répéter, t=changer sujet, q=quitter")
            continue

        choice = resolve_choice(raw, state.last_action)
        if choice is None:
            continue

        if not dispatch_choice(ui, state, choice):
            return 0

# ---------------- Main ----------------


def main() -> int:
    args = parse_args()
    ui = RichUI(Console())

    # Lazy: on ne crée le client OpenAI que si l'utilisateur le souhaite
    client = build_openai_client(ui)
    state = AppState(base=args.base_dir, client=client)

    return run_interactive(ui, state)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        Console().print("\n[red]Interrompu.[/red]")
        raise
