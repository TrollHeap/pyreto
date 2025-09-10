# services/schedule_service.py
from __future__ import annotations
from pathlib import Path
import re
from typing import List, Tuple


def build_schedule(base: Path, topic: str) -> List[Tuple[str, list[str]]]:
    """
    Regroupe <base>/exercises/<slug>/* par date dans le nom: YYYY-MM-DD-exNN.md|txt
    """
    from utils.helpers import safe_slug
    slug = safe_slug(topic)
    ex_dir = base / "exercises" / slug
    if not ex_dir.exists():
        return []
    buckets: dict[str, list[str]] = {}
    files = sorted(ex_dir.glob("*.md")) or sorted(ex_dir.glob("*.txt"))
    for f in files:
        m = re.match(r"(\d{4}-\d{2}-\d{2})-ex\d{2}\.(?:md|txt)$", f.name)
        if m:
            buckets.setdefault(m.group(1), []).append(f.name)
    return sorted((k, sorted(v)) for k, v in buckets.items())
