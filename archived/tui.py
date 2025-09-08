from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane, Header, Footer

from lib_textual.views.dashboard_view import DashboardView
from lib_textual.views.planning_view import PlanningView
from lib_textual.views.exercises_view import ExercisesView
from lib_textual.views.settings_view import SettingsView


class ParetoSystem(App):
    CSS_PATH = "./tcss/paretosystem.tcss"
    CSS_PATH = "./tcss/exercise.tcss"

    BINDINGS = [
        ("1", "show('dashboard')", "Dashboard"),
        ("2", "show('planning')", "Planning"),
        ("3", "show('ex')", "Exercises"),
        ("4", "show('settings')", "Settings"),
        ("r", "refresh_current", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(id="tabs", initial="dashboard"):
            with TabPane("Dashboard", id="dashboard"):
                yield DashboardView(id="dash")
            with TabPane("Planning", id="planning"):
                yield PlanningView(id="plan")
            with TabPane("Exercises", id="ex"):
                yield ExercisesView(id="exv")
            with TabPane("Settings", id="settings"):
                yield SettingsView(id="setv")
        yield Footer()

    # Navigation
    def action_show(self, tab_id: str) -> None:
        self.query_one("#tabs", TabbedContent).active = tab_id

    # Ex d’action “contextualisée” par page active
    def action_refresh_current(self) -> None:
        tabs = self.query_one("#tabs", TabbedContent)
        match tabs.active:            # route l’action selon l’onglet
            case "planning":
                self.query_one("#plan", PlanningView).refresh()
            case "dashboard":
                self.notify("Dashboard refreshed")
            case _:
                self.notify("Nothing to refresh here")


if __name__ == "__main__":
    app = ParetoSystem()
    app.run()
