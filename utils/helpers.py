import os
import re
import textwrap
import subprocess
from pathlib import Path


def run_cmd(cmd: list[str], *, cwd: Path | None = None) -> str:
    res = subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                         capture_output=True, text=True, check=True)
    return res.stdout


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def safe_slug(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in s.strip().lower()).strip("-")


def ensure_dirs(base: Path, topic_slug: str) -> dict[str, Path]:
    cheats_dir = base / "cheatsheets" / topic_slug
    ex_dir = base / "exercises" / topic_slug
    cheats_dir.mkdir(parents=True, exist_ok=True)
    ex_dir.mkdir(parents=True, exist_ok=True)
    return {"cheats": cheats_dir, "ex": ex_dir}


def create_exercise_files(ex_dir: Path, date_str: str, n: int, content: str | None) -> list[Path]:
    paths: list[Path] = []
    chunks: list[str] = []
    if content:
        # La regex ci-dessus peut avaler le préfixe; on re-split proprement si besoin :
        chunks = [c.strip() for c in re.findall(r'(?ms)^(?:#{1,6}\s*)?###?\s*EX\d{2}\b.*?(?=^(?:#{1,6}\s*)?###?\s*EX\d{2}\b|\Z)', content)]
    for i in range(1, n + 1):
        ident = f"ex{i:02d}"
        fname = f"{date_str}-{ident}.md"
        p = ex_dir / fname
        if content and i <= len(chunks):
            write_text(p, chunks[i - 1].rstrip() + "\n")
        else:
            skeleton = textwrap.dedent(f"""\
            ### EX{i:02d} — [Titre court façon mission]
            **Objectif (1 phrase) :**
            [ce que le héros doit accomplir]

            **Contexte (3–6 lignes) :**
            [scénario ludique + contrainte réaliste]

            **Type :** [GÉNÉRATION|DIAGNOSTIC|TRANSFORMATION|COMPARAISON|STRESS TEST]
            **Ressources :** [autorisées/interdites]

            **Entrée :**
            ```text
            [artefacts : données, logs, configs]
            ```

            **Livrables :**
            - [commande/sortie/fichier attendu]

            **Critères de victoire :**
            - [condition mesurable #1]
            - [condition mesurable #2]

            **Pièges (troupes ennemies) :**
            - [erreur typique #1]
            - [erreur typique #2]
            """).rstrip() + "\n"
            write_text(p, skeleton)
        paths.append(p)
    return paths


def create_launcher_script(ex_dir: Path, topic_slug: str) -> Path:
    sh = ex_dir / f"run_{topic_slug}.sh"
    editor = os.environ.get("EDITOR", "vi")
    content = textwrap.dedent(f"""\
    #!/usr/bin/env bash
    set -euo pipefail
    shopt -s nullglob
    DIR="$(cd -- "$(dirname -- "${{BASH_SOURCE[0]}}")" && pwd)"
    cd "$DIR"

    echo "[INFO] Exercices disponibles:"
    ls -1 *.md 2>/dev/null | sort || true

    file="${{1:-}}"
    if [[ -n "$file" && -f "$file" ]]; then
      {editor} "$file"
      exit 0
    fi

    mapfile -t files < <(ls -1 *.md 2>/dev/null | sort)
    if (( ${{#files[@]}} == 0 )); then
      echo "[WARN] Aucun fichier .md trouvé."
      exit 1
    fi

    latest="${{files[-1]}}"
    echo "[INFO] Ouverture: ${{latest}}"
    {editor} "$latest"
    """).strip() + "\n"
    write_text(sh, content)
    sh.chmod(0o755)
    return sh
