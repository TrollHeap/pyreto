from __future__ import annotations
from pathlib import Path
from typing import List, Tuple, Optional


def list_topics(base: Path) -> List[Tuple[str, Path, Optional[Path]]]:
    """
    Retourne [(slug, cheat_path, ex_dir_or_None)] en Paths.
    Convention: cheat = base/cheatsheets/<slug>/<slug>.md, ex_dir = base/exercises/<slug>
    """
    results: list[tuple[str, Path, Optional[Path]]] = []
    root = base / "cheatsheets"
    if not root.exists():
        return results
    for tdir in sorted(p for p in root.iterdir() if p.is_dir()):
        slug = tdir.name
        cheat = tdir / f"{slug}.md"
        ex_dir = base / "exercises" / slug
        results.append((slug, cheat, ex_dir if ex_dir.exists() else None))
    return results
