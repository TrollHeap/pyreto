# handlers.py
from __future__ import annotations
from pathlib import Path
from views.course_view import CourseView
from views.topics_view import TopicsView
from views.schedule_view import ScheduleView
from controllers.course_controller import CourseController
from controllers.topics_controller import TopicsController
from controllers.schedule_controller import ScheduleController
from services.cheatsheet_service import generate_cheatsheet
from services.exercises_service import generate_exercises
from utils.helpers import safe_slug

# petit utilitaire local


def _open_in_editor(path: Path) -> None:
    import os
    import subprocess
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"
    subprocess.run([editor, str(path)])


def handle_course(ui, state, topic: str) -> None:
    controller = CourseController(ui, CourseView(ui), client=state.client)
    with ui.spinner("Génération du cours…"):
        controller.run(state.base, topic)
    state.last_action = "course"


def handle_cheatsheet(ui, state, topic: str) -> None:
    with ui.spinner("Génération cheat sheet…"):
        path = generate_cheatsheet(state.base, topic, client=state.client)
    ui.console.print(f"[green]Cheat sheet:[/green] {path}")
    ui.preview_markdown(path, limit_chars=1800)
    if ui.ask_confirm("Ouvrir dans l'éditeur ?", True):
        _open_in_editor(path)
    state.last_action = "cheat"


def handle_exercises(ui, state, topic: str, n: int) -> None:
    with ui.spinner("Génération exercices…"):
        files, launcher = generate_exercises(state.base, topic, n=n, client=state.client)
    ui.console.print(f"[green]{len(files)} fichier(s)[/green] dans {files[0].parent if files else '(aucun)'}")
    if launcher:
        ui.console.print(f" Lanceur: {launcher}")
    if files and ui.ask_confirm("Prévisualiser un exercice ?", True):
        pick = ui.pick_exercise(files)
        if pick:
            _open_in_editor(pick)
    state.last_action = "ex"


def handle_topics(ui, state) -> None:
    TopicsController(ui, TopicsView(ui)).run(state.base)


def handle_schedule(ui, state, topic: str) -> None:
    ex_dir = state.base / "exercises" / safe_slug(topic)
    ScheduleController(ui, ScheduleView(ui)).run(ex_dir, topic)
