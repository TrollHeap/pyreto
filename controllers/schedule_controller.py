from services.schedule_service import build_schedule


class ScheduleController:
    def __init__(self, ui, view):  # view = ScheduleView
        self.ui, self.view = ui, view

    def run(self, ex_dir, slug: str):
        sched = build_schedule(ex_dir)
        self.view.show(sched, slug)
