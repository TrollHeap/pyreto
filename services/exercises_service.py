from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
from api.prompt import build_exercises_prompt
from utils.helpers import ensure_dirs, safe_slug, create_exercise_files, create_launcher_script


def generate_exercises(base: Path, topic: str, n: int = 5, *, client: Optional[object] = None) -> Tuple[List[Path], Path]:
    """
    Crée des fichiers sous <base>/exercises/<slug> et un lanceur.
    """
    slug = safe_slug(topic)
    dirs = ensure_dirs(base, slug)
    date_str = datetime.now().strftime("%Y-%m-%d")

    content: Optional[str] = None
    if client:
        content = (client.generate(input_text=build_exercises_prompt(topic, n)) or "").strip()

    files = create_exercise_files(dirs["ex"], date_str, n, content)
    launcher = create_launcher_script(dirs["ex"], slug)
    return files, launcher
