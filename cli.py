#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

from api.openai import OpenAIResponder, OpenAIConfig
from core import ParetoLearningSystem
from rich_ui.ui_rich import RichUI

from rich.console import Console

PATH_DIR="Developer/exercise/pareto"

def build_client_from_args(args) -> OpenAIResponder | None:
    try:
        return OpenAIResponder(OpenAIConfig(
            model=args.model,
            instructions=args.instructions,
            prompt_id=args.prompt_id,
            prompt_version=args.prompt_version,
            prompt_vars=json.loads(args.prompt_vars) if args.prompt_vars else None,
        ))
    except Exception:
        return None

def run_interactive(ui: RichUI, base_dir: Path, client: OpenAIResponder | None) -> int:
    choice = ui.show_menu()
    if choice == "7":
        ui.console.print("[bold]Au revoir! 👋[/bold]"); return 0
    if client is None:
        # Option de config rapide
        client = ui.ask_openai_client()

    system = ParetoLearningSystem(base_dir=base_dir, client=client)

    # Saisies minimales selon choix
    if choice in {"1","2","3","4","6"}:
        topic = ui.ask_text("Sujet ?")
    if choice == "1":
        n = ui.ask_int("Combien d'exercices ?", 5)
        with ui.spinner("Génération du cours…") as p: p.add_task("gen", total=None)
        result = system.auto_generate_full_course(topic, n=n)
        ui.show_course_summary(result["cheatsheet"], result["ex_dir"], result["manifest"])
    elif choice == "2":
        with ui.spinner("Cheat sheet…") as p: p.add_task("gen", total=None)
        path = system.generate_cheatsheet(topic)
        ui.show_cheatsheet_created(path)
    elif choice == "3":
        n = ui.ask_int("Combien d'exercices ?", 5)
        with ui.spinner("Exercices…") as p: p.add_task("gen", total=None)
        files, launcher = system.generate_exercises(topic, n)
        ui.show_exercises_created(files, launcher)
    elif choice == "4":
        ctx = system.practice_context(topic)
        cheat = ctx["cheatsheet"]; files = ctx["files"]
        mode = ui.ask_text("Mode (g=guidé, e=examen)", "g")
        if mode == "g" and cheat: ui.preview_markdown(cheat)
        pick = ui.pick_exercise(files)
        if pick: ui.open_in_editor(pick)
    elif choice == "5":
        ui.show_topics(system.list_topics())
    elif choice == "6":
        sched = system.review_schedule(topic)
        from utils.helpers import safe_slug
        ui.show_schedule(sched, safe_slug(topic))
    return 0

def main() -> int:
    console = Console()             # <<< une seule instance
    ui = RichUI(console)                # injectée partout dans l’UI

    home = Path.home()
    default_base = home / PATH_DIR

    ap = argparse.ArgumentParser(description="Pareto Learning (OpenAI)")
    ap.add_argument("topic", nargs="?", help="Sujet à apprendre (ex: awk)")
    ap.add_argument("-n", "--num-ex", type=int, default=5, help="Nombre d'exercices (défaut: 5)")
    ap.add_argument("-b", "--base-dir", type=Path, default=default_base)
    ap.add_argument("--model", default="gpt-5")
    ap.add_argument("--instructions", default="Tu es concis, précis, et technique.")
    ap.add_argument("--prompt-id"); ap.add_argument("--prompt-version"); ap.add_argument("--prompt-vars")
    args = ap.parse_args()

    client = build_client_from_args(args)

    # Mode interactif (aucun topic fourni)
    if args.topic is None and len(sys.argv) == 1:
        return run_interactive(ui, args.base_dir, client)

    # Mode non interactif
    topic = args.topic.strip()
    system = ParetoLearningSystem(base_dir=args.base_dir, client=client)
    with ui.spinner("Génération du cours…") as p: p.add_task("gen", total=None)
    result = system.auto_generate_full_course(topic, n=args.num_ex)
    ui.show_course_summary(result["cheatsheet"], result["ex_dir"], result["manifest"])
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        Console().print("\n[red]Interrompu.[/red]")
        raise
