import npyscreen

from app.config import Widget


class Event:
    ON_FILTER_CHANGE = "onFilterChange"

    def event(self: Widget, event: str):
        if hasattr(self, "parentApp"):
            self.parentApp.queue_event(npyscreen.Event(event))
        elif hasattr(self, "parent"):
            self.parent.event(event)
