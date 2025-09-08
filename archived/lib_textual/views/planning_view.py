from textual.app import ComposeResult
from textual.widgets import   Static, Input 
from textual.containers import Vertical, Horizontal, VerticalScroll

class PlanningView(Vertical):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Input(placeholder="Filter week…", id="plan-filter"),
            Static("⟳", id="plan-refresh"),
            id="plan-toolbar",
        )
        with VerticalScroll(id="plan-body"):
            for d in ["Mon","Tue","Wed","Thu","Fri"]:
                yield Static(f"• {d}: study blocks", classes="plan-item")
    # def refresh(self) -> None:
    #     self.query_one("#plan-body").mount(Static("• Sat/Sun: rest"))
