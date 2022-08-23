#!/usr/bin/python3.9
import weakref

import npyscreen
from typing import TypedDict, ClassVar

from filters import FiltersPreview, FilterForm
from config import read_config
from box.grid import Grid, Box


class Display:
    CORRECTION: ClassVar[int] = 2
    DisplayConfig = TypedDict("DisplayConfig", {
        "right": TypedDict("__RightBar", {
            "top": TypedDict("__Top", {"max_width": int, "max_height": int}),
            "bottom": TypedDict("__Bottom", {"max_width": int, "max_height": int, "rely": int}, total=False),
        }),
        "left": TypedDict("__LeftBar", {"relx": int, "rely": int})
    })

    def __init__(self, vertical_line: float, ratio: float, usable_space: tuple[int, int]):
        if vertical_line < 0 or vertical_line > 1:
            raise ValueError("vertical_line must be between 0 and 1")

        self.width = usable_space[1]
        self.height = usable_space[0]
        self.vertical_line = vertical_line
        self.right = self.RightBar(ratio)
        self.left = self.LeftBar()

    class RightBar:
        """Serves filters and other right-side widgets."""

        def __init__(self, ratio: float):
            """Rates how top box's size is related to second"""
            self.top: float or None = None
            self.bottom: float or None = None
            self.__set_relation(ratio)

        def __set_relation(self, ratio: float):
            """Sets new relation between top and bottom boxes"""
            if ratio < 0:
                raise ValueError("Ratio must be higher than 0")
            elif ratio < 1:
                self.top = 1
                self.bottom = self.top / ratio
            elif ratio > 1:
                self.bottom = 1
                self.top = ratio
            else:
                self.top = 1
                self.bottom = 1

        def __call__(self) -> tuple[float, float]:
            """Returns top and bottom boxes' sizes"""
            total = self.top + self.bottom
            return self.top / total, self.bottom / total

    class LeftBar:
        pass

    def __call__(self) -> DisplayConfig:
        top, bottom = self.right()
        return {
            "right": {
                "top": {
                    "max_width": self.width - int(self.width * self.vertical_line) - self.CORRECTION,
                    "max_height": int(self.height * top),
                },
                "bottom": {
                    "rely": int(self.height * top) + self.CORRECTION,
                    "max_width": self.width - int(self.width * self.vertical_line) - self.CORRECTION,
                },
            },
            "left": {
                "relx": self.width - int(self.width * self.vertical_line),
                "rely": self.CORRECTION,
            },
        }


class Combo(npyscreen.ComboBox):
    name = "Combo"
    values = ['1', '2']
    value = None


class FixedText(npyscreen.TitleText):
    name = "Name"
    value = "lasld"


class KWMainForm(npyscreen.FormBaseNew):
    def __init__(self, *args, config, **kwargs):
        self.config = config
        self._filters = {}

        super().__init__(*args, **kwargs)

    def create(self):
        display_config = Display(
            vertical_line=self.config["panel_resolution"]["vertical_line"],
            ratio=(self.config["panel_resolution"]["right"]["top"] / self.config["panel_resolution"]["right"][
                "bottom"]),
            usable_space=self.useable_space()
        )()

        self.filters = self.add(Box, contained_widget_arguments={"values": [[0, 1, 2], [None, 0, 1, 2], [None, 0, 1, 2], [None, 0, 1, 2], [None, 0, 1, 2], [None, 0, 1, 2]], "filters": self.config["filters"]}, **display_config["right"]["top"])
        self.description = self.add(npyscreen.BoxTitle, name="description", **display_config["right"]["bottom"])
        self.bulk = self.add(npyscreen.BoxTitle, name="left", **display_config["left"])

        self.add_handlers({
            "^Q": self.exit_application,
            "^E": self.edit_config,
            "^S": self.edit_config,
        })

    # def fill_filters(self):
    #     for filter in self.config["filters"]:
    #         self.filters.values.append(filter)
    #         self.filters.value = filter
    #         self.filters.display()

    def on_filter_change(self, event):
        self.display()

    def edit_config(self, event):
        self.parentApp.switchForm("Filters")

    def exit_application(self, *args, **kwargs):
        self.parentApp.switchForm(None)

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)


class KWApplication(npyscreen.NPSAppManaged):
    def __init__(self):
        config = read_config()

        self.meta = config["metadata"]
        self.app_config = config["data"]

        super(KWApplication, self).__init__()

    def onStart(self):
        self.main = self.addForm(
            f_id="MAIN",
            FormClass=KWMainForm,
            name=f"{self.meta['name']} v{self.meta['version']}",
            config=self.app_config
        )

        self.filters = self.addForm(
            f_id="Filters",
            FormClass=FilterForm,
            name=f"filters",
            config=self.app_config
        )



if __name__ == '__main__':
    try:
        a = KWApplication()
        a.run()
    except KeyboardInterrupt:
        exit(0)

