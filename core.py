#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from datetime import datetime
from pathlib import Path
import re
from typing import Optional

from api.prompt import build_cheatsheet_prompt, build_exercises_prompt
from api.openai import OpenAIResponder
from utils.helpers import (
    ensure_dirs, safe_slug, write_text, create_exercise_files,
    create_launcher_script, write_manifest,
)


class ParetoLearningSystem:
    """Aucune dépendance à Rich ici. Pas d'I/O terminal. Retourne des valeurs pures."""

    def __init__(self, base_dir: Path, client: Optional[OpenAIResponder]) -> None:
        self.base_dir = base_dir
        self.client = client  # None => placeholders

    # --- internes ---

    def _generate_or_none(self, prompt: str) -> Optional[str]:
        if self.client is None:
            return None
        return self.client.generate(input_text=prompt)

    # --- API publique ---

    def generate_cheatsheet(self, topic: str) -> Path:
        slug = safe_slug(topic)
        dirs = ensure_dirs(self.base_dir, slug)
        path = dirs["cheats"] / f"{slug}.md"

        content = self._generate_or_none(build_cheatsheet_prompt(topic))
        if not content:
            placeholder = (
                f"# {topic} — Cheat Sheet Pareto (PLACEHOLDER)\n"
                f"> OpenAI non configuré. Utilise ce prompt :\n\n```\n"
                f"{build_cheatsheet_prompt(topic)}\n```\n"
            )
            content = placeholder
        write_text(path, content.rstrip() + "\n")
        return path

    def generate_exercises(self, topic: str, n: int = 5) -> tuple[list[Path], Path]:
        slug = safe_slug(topic)
        dirs = ensure_dirs(self.base_dir, slug)
        date_str = datetime.now().strftime("%Y-%m-%d")

        content = self._generate_or_none(build_exercises_prompt(topic, n))
        files = create_exercise_files(dirs["ex"], date_str, n, content)
        launcher = create_launcher_script(dirs["ex"], slug)
        return files, launcher

    def auto_generate_full_course(self, topic: str, n: int = 5) -> dict:
        cheat = self.generate_cheatsheet(topic)
        ex_files, _ = self.generate_exercises(topic, n)
        slug = safe_slug(topic)
        manifest = write_manifest(self.base_dir, topic, slug, cheat.parent, ex_files)
        return {"cheatsheet": cheat, "ex_dir": ex_files[0].parent if ex_files else None, "manifest": manifest}

    def list_topics(self) -> list[tuple[str, Path, Optional[Path]]]:
        base = self.base_dir
        topics: list[tuple[str, Path, Optional[Path]]] = []
        root = base / "cheatsheets"
        if root.exists():
            for tdir in sorted(root.glob("*")):
                slug = tdir.name
                cheat = root / slug / f"{slug}.md"
                ex_dir = base / "exercises" / slug
                topics.append((slug, cheat, ex_dir if ex_dir.exists() else None))
        return topics

    def review_schedule(self, topic: str) -> list[tuple[str, list[str]]]:
        slug = safe_slug(topic)
        ex_dir = self.base_dir / "exercises" / slug
        if not ex_dir.exists():
            return []
        buckets: dict[str, list[str]] = {}
        files = sorted(ex_dir.glob("*.md")) or sorted(ex_dir.glob("*.txt"))
        for f in files:
            m = re.match(r"(\d{4}-\d{2}-\d{2})-ex\d{2}\.(?:md|txt)$", f.name)
            if m:
                buckets.setdefault(m.group(1), []).append(f.name)
        return sorted((k, sorted(v)) for k, v in buckets.items())

    def practice_context(self, topic: str) -> dict:
        """Renvoie tout ce qu'il faut pour la pratique ; l'UI décide comment l'afficher."""
        slug = safe_slug(topic)
        ex_dir = self.base_dir / "exercises" / slug
        cheat = self.base_dir / "cheatsheets" / slug / f"{slug}.md"
        files = sorted(ex_dir.glob("*.md")) or sorted(ex_dir.glob("*.txt"))
        return {"cheatsheet": cheat if cheat.exists() else None, "files": files}
