# controllers/course_controller.py
from pathlib import Path
from services.course_service import generate_course


class CourseController:
    def __init__(self, ui, view, client=None):
        self.ui, self.view, self.client = ui, view, client

    def run(self, base: Path, slug: str):
        result = generate_course(base, slug, client=self.client)
        self.view.show_created(result["cheatsheet"], result["ex_dir"], result.get("manifest"))
