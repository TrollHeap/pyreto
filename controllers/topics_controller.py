from services.topics_service import list_topics


class TopicsController:
    def __init__(self, ui, view):  # view = TopicsView
        self.ui, self.view = ui, view

    def run(self, base):
        topics = list_topics(base)
        self.view.show(topics)
