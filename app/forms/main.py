import npyscreen

from ..config import Config, Filter
from ..config import Display

from .box.grid import Box
from .box.bulk import BulkBox
from ..event import Event


class KWMainForm(npyscreen.FormBaseNew, Event):
    def __init__(self, *args, config, **kwargs):
        self.config: Config = config
        self._filters = {}

        super().__init__(*args, **kwargs)

    def create(self):
        def iter_filter_values(filters: dict[str, Filter]):
            for _, _filter in filters.items():
                yield [_filter["selected"]] + [i for i in range(len(_filter["options"]))]

        display_config = Display(
            vertical_line=self.config["panel_resolution"]["vertical_line"],
            ratio=(self.config["panel_resolution"]["right"]["top"] / self.config["panel_resolution"]["right"][
                "bottom"]),
            usable_space=self.useable_space()
        )()

        self.filters = self.add(Box, contained_widget_arguments={
            "values": [
                # TODO: values by config
                *iter_filter_values(self.config["filters"])
            ],
            "filters": self.config["filters"]},
                                **display_config["right"]["top"])
        self.description = self.add(npyscreen.BoxTitle, name="description", **display_config["right"]["bottom"])
        self.bulk = self.add(
            BulkBox,
            contained_widget_arguments={
                "name": "bulk",
                "values": ["Bas", "Foo"],
                "filters": self.config["filters"],
            },
            name="left",
            **display_config["left"]
        )

        self.add_handlers({
            "^Q": self.exit_application,
            "^E": self.filter_change,
            "^S": self.filter_change,
        })

    def _test_safe_to_exit(self):
        return True

    def filter_change(self, event):
        self.h_exit_down(event)
        self.handle_exiting_widgets(npyscreen.widget.EXITED_DOWN)
        self.event(self.ON_FILTER_CHANGE)

    def exit_application(self, *args, **kwargs):
        self.parentApp.switchForm(None)

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)
