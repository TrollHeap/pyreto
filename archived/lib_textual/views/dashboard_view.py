from textual.app import ComposeResult
from textual.widgets import Static, Input, DataTable 
from textual.containers import Vertical, VerticalScroll

# TODO: Dashboard general metrics, not just uptime/load/errors

class DashboardView(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Static("📊 Metrics", id="dash-title")
        table = DataTable(id="dash-table"); table.add_columns("Metric", "Value")
        table.add_rows([("Uptime", "12d"), ("Load", "0.42"), ("Errors", "0")])
        yield table
    def on_show(self) -> None:        # appelé quand l’onglet devient visible
        self.query_one("#dash-title", Static).update("📊 Metrics (active)")
