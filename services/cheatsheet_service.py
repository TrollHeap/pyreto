# services/cheatsheet_service.py
from __future__ import annotations
from pathlib import Path
from typing import Optional
from api.prompt import build_cheatsheet_prompt
from utils.helpers import ensure_dirs, safe_slug, write_text


def generate_cheatsheet(base: Path, topic: str, *, client: Optional[object] = None) -> Path:
    """
    Crée <base>/cheatsheets/<slug>/<slug>.md.
    Si client est fourni, génère via LLM, sinon placeholder.
    """
    slug = safe_slug(topic)
    dirs = ensure_dirs(base, slug)  # doit créer base/cheatsheets/<slug> et base/exercises/<slug>
    path = dirs["cheats"] / f"{slug}.md"

    prompt = build_cheatsheet_prompt(topic)
    if client:
        content = (client.generate(input_text=prompt) or "").strip()
        if not content:
            content = f"# {topic} — Cheat Sheet (vide)\n"
    else:
        content = (
            f"# {topic} — Cheat Sheet Pareto (PLACEHOLDER)\n"
            f"> OpenAI non configuré. Utilise ce prompt :\n\n```\n{prompt}\n```\n"
        )
    write_text(path, content.rstrip() + "\n")
    return path
