from __future__ import annotations
from pathlib import Path
from typing import Iterable

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import (
    Static, Select, Markdown, Button, TextArea, ListView, ListItem,
    TabbedContent, TabPane, Label, Log
)
from textual.containers import Vertical, VerticalScroll, Horizontal, Container
from textual import events

# --- Chemins (ajuste si besoin) ---
BASE = Path("/home/trollheap/Developer/exercise/pareto")
DIR_EX = BASE / "exercises"
DIR_CS = BASE / "cheatsheets"

PLACEHOLDER_INSTR = "_Sélectionne un exercice à gauche._"
PLACEHOLDER_SHEET = "_Aucun cheatsheet trouvé pour ce sujet._"   # <-- sans ### !

STARTER_CODE = "def sum2(a, b):\n    return a + b\n"


class ExercisesView(Vertical):
    BINDINGS = [
        ("f5", "run_code", "Run"),
        ("ctrl+s", "submit_code", "Submit"),
        ("j", "next_item", "Next ex"),
        ("k", "prev_item", "Prev ex"),
        ("escape", "focus_editor", "Focus editor"),
    ]

    # Etat réactif simple
    selected_topic: reactive[str] = reactive("", init=False)
    selected_file: reactive[Path | None] = reactive(None)
    is_running: reactive[bool] = reactive(False)

    # cache courant des fichiers listés (index -> Path)
    _current_files: list[Path] = []

    def compose(self) -> ComposeResult:
        with Horizontal(id="root"):
            with Vertical(id="left"):
                yield Static("🧪 Exercises", id="left-title")
                yield Select([], id="ex-select-left")  # options injectées au mount
                yield ListView(id="ex-list")

            with Container(id="center"):
                yield Static("Editor", id="editor-title")
                with Container(id="editor-wrap"):
                    yield TextArea.code_editor(STARTER_CODE, language="python", id="editor")
                with Horizontal(id="toolbar"):
                    yield Button("Run (F5)", id="btn-run", variant="primary")
                    yield Button("Submit (Ctrl+S)", id="btn-submit", variant="success")

            with Vertical(id="right"):
                yield Static("📘 Reference", id="right-title")
                with TabbedContent(id="ref-tabs"):
                    with TabPane("Cheatsheet", id="tab-cheatsheet"):
                        yield VerticalScroll(Markdown(PLACEHOLDER_SHEET, id="sheet"))
                    with TabPane("Instructions", id="tab-instructions"):
                        yield VerticalScroll(Markdown(PLACEHOLDER_INSTR, id="instructions"))
                    with TabPane("Results", id="tab-results"):
                        yield Log(id="results-log")

    # -------- Lifecycle --------
    def on_mount(self) -> None:
        """Scan du FS et initialisation UI une fois la vue montée."""
        topics = self._scan_topics()
        select = self.query_one("#ex-select-left", Select)
        select.set_options([(t, t) for t in topics])

        # Choix par défaut: premier sujet s'il existe
        if topics:
            self.selected_topic = topics[0]
            select.value = topics[0]
            self._reload_topic(topics[0])
        else:
            # Aucun sujet -> vide
            self._fill_list([])
            self._set_cheatsheet(None)
            self._set_instructions(None)

    # -------- FS helpers --------
    def _scan_topics(self) -> list[str]:
        """Liste les dossiers de exercises/* comme sujets."""
        if not DIR_EX.exists():
            return []
        return sorted([p.name for p in DIR_EX.iterdir() if p.is_dir()])

    def _list_ex_files(self, topic: str) -> list[Path]:
        """Ex: exercises/<topic>/*.md|*.txt triés par nom."""
        root = DIR_EX / topic
        if not root.exists():
            return []
        files = sorted([*root.glob("*.md"), *root.glob("*.txt")])
        return files

    def _read_text(self, path: Path | None) -> str:
        if not path or not path.exists():
            return ""
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return path.read_text(errors="ignore")

    def _cheatsheet_path(self, topic: str) -> Path | None:
        p = DIR_CS / topic / f"{topic}.md"
        return p if p.exists() else None

    # -------- UI helpers --------
    def _fill_list(self, files: list[Path]) -> None:
        """Remplit la ListView avec les noms de fichiers (sans chemin)."""
        lv = self.query_one("#ex-list", ListView)
        lv.clear()
        items = [ListItem(Label(f.name)) for f in files]
        self._current_files = files
        if items:
            lv.extend(items)
            # mettre le curseur en haut pour déclencher Highlighted
            lv.index = 0
        else:
            # aucune entrée
            pass

    def _set_instructions(self, path: Path | None) -> None:
        md = self.query_one("#instructions", Markdown)
        content = self._read_text(path).strip()
        md.update(content if content else PLACEHOLDER_INSTR)

    def _set_cheatsheet(self, path: Path | None) -> None:
        md = self.query_one("#sheet", Markdown)
        content = self._read_text(path).strip()
        md.update(content if content else PLACEHOLDER_SHEET)

    def _reload_topic(self, topic: str) -> None:
        """Charge la liste d’exos et le cheatsheet pour un sujet."""
        # Titre
        self.query_one("#left-title", Static).update(f"🧪 Exercises — {topic}")
        # Liste des exos
        files = self._list_ex_files(topic)
        self._fill_list(files)
        # Cheatsheet
        self._set_cheatsheet(self._cheatsheet_path(topic))
        # Reset instructions
        self.selected_file = None
        self._set_instructions(None)
        # Focus sur la liste pour UX rapide
        self.query_one("#ex-list", ListView).focus()

    # -------- Actions --------
    def action_run_code(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        log = self.query_one("#results-log", Log)
        editor = self.query_one("#editor", TextArea)
        log.write("⏱ Run request received. Evaluating (stub)…")
        log.write(f"[dim]Source length: {len(editor.text)} chars[/]")
        self.query_one("#ref-tabs", TabbedContent).active = "tab-results"
        self.is_running = False

    def action_submit_code(self) -> None:
        log = self.query_one("#results-log", Log)
        editor = self.query_one("#editor", TextArea)
        log.write("📤 Submit: sending to evaluator [stub]…")
        log.write(f"[dim]Payload size: {len(editor.text)} chars[/]")
        self.query_one("#ref-tabs", TabbedContent).active = "tab-results"

    def action_focus_editor(self) -> None:
        self.query_one("#editor", TextArea).focus()

    def action_next_item(self) -> None:
        self.query_one("#ex-list", ListView).action_cursor_down()

    def action_prev_item(self) -> None:
        self.query_one("#ex-list", ListView).action_cursor_up()

    # -------- Handlers --------
    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "btn-run":
            self.action_run_code()
        elif e.button.id == "btn-submit":
            self.action_submit_code()

    def on_select_changed(self, e: Select.Changed) -> None:
        if e.select.id == "ex-select-left":
            # met à jour le sujet + recharge FS
            self.selected_topic = e.value
            if self.is_mounted:
                self._reload_topic(e.value)

    def on_list_view_highlighted(self, e: ListView.Highlighted) -> None:
        """Prévisualiser dès que le curseur change (↑/↓)."""
        if e.list_view.id != "ex-list" or not self._current_files:
            return
        idx = e.list_view.index
        if 0 <= idx < len(self._current_files):
            path = self._current_files[idx]
            self.selected_file = path
            self._set_instructions(path)
            self.query_one("#editor-title", Static).update(f"Editor — {path.name}")
            # Bascule sur l’onglet Instructions (prévisu)
            self.query_one("#ref-tabs", TabbedContent).active = "tab-instructions"

    def on_list_view_selected(self, e: ListView.Selected) -> None:
        """Confirme la sélection (Enter/clic) — même logique que Highlighted."""
        if e.list_view.id != "ex-list" or not self._current_files:
            return
        idx = e.list_view.index
        if 0 <= idx < len(self._current_files):
            path = self._current_files[idx]
            self.selected_file = path
            self._set_instructions(path)
            self.query_one("#editor-title", Static).update(f"Editor — {path.name}")
            self.query_one("#ref-tabs", TabbedContent).active = "tab-instructions"

    # -------- Réactions --------
    def watch_selected_topic(self, topic: str) -> None:
        """Ne touche à l’UI que si la vue est montée."""
        if not self.is_mounted or not topic:
            return
        # (On laisse la logique principale dans _reload_topic)
