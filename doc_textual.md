## 🧙 Le Grimoire du Mage Textual

*Apprendre à maîtriser Textual comme un héros apprend sa magie*

---

## 1. ⚔️ Qu’est-ce que Textual ?

Textual est une bibliothèque Python pour construire des **interfaces TUI** (Terminal User Interfaces) avec :

* **Widgets** (boutons, labels, digis, listes…)
* **Layout** (containers horizontaux/verticaux, scrollables…)
* **Réactivité** (`reactive` pour suivre des changements)
* **Événements** (`on_event`, `watch_x`)
* **Actions** (`action_foo` liées à des raccourcis clavier)

💡 Pense à Textual comme à **un moteur de jeu dans ton terminal** :

* Tu as une **scène** (App)
* Des **unités** (Widgets)
* Des **règles** (réactivité, événements)
* Des **compétences** (Actions + Bindings clavier)

---

## 2. 🏰 Architecture Textual (schéma global)

```ascii
┌──────────────┐
│   App        │  ← ton jeu / application
│──────────────│
│  Containers  │  ← layouts (Vertical, Horizontal, Scroll…)
│──────────────│
│  Widgets     │  ← boutons, labels, Digits, etc.
└──────────────┘
        │
        ▼
Événements / Actions (clavier, souris, timers)
```

---

## 3. 📜 Les concepts magiques

### 3.1. Reactive

Déclare une variable suivie automatiquement :

```python
from textual.reactive import reactive

class MyWidget(Widget):
    counter = reactive(0)

    def watch_counter(self, value: int) -> None:
        self.update(f"Compteur = {value}")
```

* `counter` change → déclenche `watch_counter`.

---

### 3.2. Timers

Textual peut exécuter du code régulièrement :

```python
def on_mount(self):
    self.set_interval(1.0, self.tick)

def tick(self):
    self.counter += 1
```

---

### 3.3. Events

Les widgets envoient des signaux :

```python
def on_button_pressed(self, event: Button.Pressed):
    if event.button.id == "start":
        self.start()
```

---

### 3.4. Actions + Bindings

Relie une touche clavier à une méthode :

```python
class MyApp(App):
    BINDINGS = [("q", "quit", "Quitter l'app")]

    def action_quit(self):
        self.exit()
```

---

## 4. ⏱ Exemple : le Stopwatch

### 4.1. TimeDisplay = moteur du chrono

* Stocke `start_time`, `total`, `time`.
* Calcule `time = total + (monotonic() - start_time)`.
* Réagit au changement (`watch_time`) → affiche `HH:MM:SS`.

```ascii
Start ─► [monotonic → start_time]
Tick  ─► time = total + (now - start_time)
Stop  ─► total += (now - start_time), pause tick
Reset ─► total = 0, time = 0
```

---

### 4.2. Stopwatch = UI

* Boutons `Start`, `Stop`, `Reset`
* Connecte les boutons → appelle méthodes du `TimeDisplay`.

```ascii
[Start][Stop][Reset] ──► [TimeDisplay chrono]
```

---

### 4.3. StopwatchApp = le terrain de jeu

* Compose plusieurs `Stopwatch` dans un `VerticalScroll`.
* Ajoute des actions clavier (`a`, `r`, `d`) :

  * `a` = add stopwatch
  * `r` = remove stopwatch
  * `d` = dark mode toggle

---

## 5. 🗡️ Entraînement pratique

### Étape 1 — Hello Widget

Crée une app minimale :

```python
from textual.app import App

class HelloApp(App):
    def compose(self):
        yield Label("Hello Textual!")

HelloApp().run()
```

### Étape 2 — Reactive

Ajoute un compteur qui augmente avec une touche :

```python
from textual.reactive import reactive
from textual.widgets import Label

class Counter(Label):
    count = reactive(0)

    def watch_count(self, v: int): self.update(str(v))

class CounterApp(App):
    BINDINGS = [("space", "inc", "Increment")]
    def compose(self): yield Counter()
    def action_inc(self): self.query_one(Counter).count += 1

CounterApp().run()
```

### Étape 3 — Chrono

Reprends `TimeDisplay` + boutons. Vérifie :

* Démarrage → le temps s’écoule
* Stop → le temps fige
* Reset → tout repart à 0

---

## 6. 🎮 Carte mentale

```ascii
TEXTUAL
│
├─ App (racine)
│   ├─ compose() : crée l’arbre
│   ├─ BINDINGS : raccourcis clavier
│   └─ action_* : méthodes liées
│
├─ Containers
│   ├─ Horizontal / Vertical
│   └─ Scroll
│
├─ Widgets
│   ├─ Boutons
│   ├─ Labels / Digits
│   └─ Custom (hérités)
│
├─ Reactive : suivi automatique de l’état
├─ Events : on_button_pressed, on_mount, etc.
└─ Timers : set_interval, set_timeout
```

---

## 7. 🧭 Checklist pour maîtriser Textual

* [ ] Créer un widget réactif (`reactive` + `watch_x`).
* [ ] Lancer un `set_interval` pour rafraîchir l’UI.
* [ ] Réagir à un événement bouton ou clavier.
* [ ] Structurer avec des containers (`HorizontalGroup`, `VerticalScroll`).
* [ ] Gérer plusieurs instances d’un même widget (ex: multiples chronos).
* [ ] Ajouter des raccourcis clavier (`BINDINGS`).

---

## 8. ⚡ Astuce finale

**Toujours séparer :**

* *Moteur logique* (calculs, chrono)
* *UI Textual* (widgets, events, bindings)

Ainsi tu peux tester ton moteur en **pur Python** sans Textual, puis brancher l’UI.

---

👉 Veux-tu que je te construise un **mini-projet d’exercices progressifs** (format quêtes comme tes prompts gamifiés) pour apprendre Textual en 5 étapes pratiques ?
