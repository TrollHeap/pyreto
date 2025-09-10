# services/course_service.py
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any
from services.cheatsheet_service import generate_cheatsheet
from services.exercises_service import generate_exercises


def generate_course(base: Path, topic: str, *, client: Optional[object] = None) -> Dict[str, Any]:
    """
    Génère cheat + exos. Retourne {"cheatsheet": Path, "ex_dir": Path | None, "manifest": Path | None}
    (manifest None si tu ne le gères pas encore).
    """
    cheat = generate_cheatsheet(base, topic, client=client)
    files, _launcher = generate_exercises(base, topic, n=5, client=client)
    ex_dir = files[0].parent if files else None
    return {"cheatsheet": cheat, "ex_dir": ex_dir, "manifest": None}
