import textwrap

# ================== Prompts (LLM) ==================


def build_cheatsheet_prompt(topic: str) -> str:

    return textwrap.dedent(f"""\
    Tu es un expert pédagogique.
    Ta tâche : produire un **cheat sheet Pareto (20/80)** en **français** sur le sujet "{topic}", au **format EXACT** ci-dessous.

    **Règles impératives :**
    - En-tête sur 3 lignes avec `# ==============================================`
    - Sujet en majuscules suivi de `80/20 CHEAT SHEET`
    - ≤ 10 sections principales
    - Chaque titre de section commence par `##` suivi d’un emoji et d’un titre concis
    - Après chaque section : une ligne seule contenant `---`
    - **Tous les exemples dans des blocs de code** avec syntaxe appropriée (`bash`, `text`, `sql`, etc.)
    - Style concis : phrases courtes, pas de paragraphes inutiles
    - Pas d’intro ni de conclusion
    - Terminer par un bloc final **⚡ 5 Commandes Pareto ultra-utiles ⚡** avec 5 lignes numérotées
    - Les commandes doivent être directement exécutables ou immédiatement applicables
    - Si possible, utiliser des séparateurs visuels (`---`) entre sections
    """).strip()


def build_exercises_prompt(topic: str, n: int) -> str:
    return textwrap.dedent(f"""\
    🎮 Contexte :
    Tu es un maître stratège dans un univers inspiré de *Warcraft 3*.
    Les étudiants sont des héros en campagne, et chaque exercice est une **quête** progressive pour
    gagner en puissance (maîtrise de "{topic}").

    ## ⚔️ Règles de la campagne
    - Génère {n} quêtes numérotées : **EX01..EX{n:02d}**
    - Jamais de solution donnée
    - Difficulté **croissante**
    - Alterner les types de quêtes :
      *GÉNÉRATION · DIAGNOSTIC · TRANSFORMATION · COMPARAISON · STRESS TEST*
    - Chaque quête doit être **auto-suffisante** (données fournies)
    - Format en **Markdown**, avec blocs d’entrée en ```text
    - Max ~180 mots par quête

    ## 🛡️ Format d’une quête
    ### EX01 — [Titre court façon mission]
    **Objectif (1 phrase) :**
    [ce que le héros doit accomplir]

    **Contexte (3–6 lignes) :**
    [scénario ludique + contrainte réaliste]

    **Type :** [GÉNÉRATION|DIAGNOSTIC|TRANSFORMATION|COMPARAISON|STRESS TEST]
    **Ressources :** [autorisées/interdites]

    **Entrée :**
    ```text
    [artefacts à manipuler : données, logs, configs]
    ```

    **Livrables :**
    - [commande/sortie/fichier attendu]

    **Critères de victoire :**
    - [condition mesurable #1]
    - [condition mesurable #2]

    **Pièges (troupes ennemies) :**
    - [erreur typique #1]
    - [erreur typique #2]

    ## 🧭 Rendu attendu
    Les {n} quêtes au format ci-dessus, de **EX01** à **EX{n:02d}**.
    """).strip()
