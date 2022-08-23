#!/usr/bin/python3.9
import weakref

import npyscreen
from typing import TypedDict, ClassVar

from config import read_config


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


class Box(npyscreen.BoxTitle):
    _contained_widget = FixedText
    name = "Box"

    def make_contained_widget(self, contained_widget_arguments=None):
        self._my_widgets = []
        for i in range(12):
            if contained_widget_arguments:
                self._my_widgets.append(self._contained_widget(self.parent,
                                                               rely=self.rely + 1 + i, relx=self.relx + 2,
                                                               max_width=self.width - 4, max_height=self.height - 2,
                                                               **contained_widget_arguments
                                                                   ))

            else:
                self._my_widgets.append(self._contained_widget(self.parent,
                                                               rely=self.rely + 1 + i, relx=self.relx + 2,
                                                               max_width=self.width - 4, max_height=self.height - 2,
                                                       ))
        self.entry_widget = weakref.proxy(self._my_widgets[0])
        self.entry_widget.parent_widget = weakref.proxy(self)


class GridColTitles(npyscreen.SimpleGrid):
    _contained_widgets = Combo
    default_column_number = 1
    name = 'GridColTitles'

    def __init__(self, *args, **kwargs):
        super(GridColTitles, self).__init__(*args, **kwargs)
        self.values = [[0,1,2],[0,1,2, 'kjljl']]

    def make_contained_widgets(self):
        self.values = [[[]], [[]]]
        self._my_widgets = []
        self.columns = self.default_column_number
        y_offset = 0
        for col in range(len(self.values)):
            self._my_widgets.append(
                [
                    self._contained_widgets(
                        self.parent, values=["14", "15", "16"], value=1, rely=self.rely + y_offset + self.additional_y_offset,
                        relx=self.relx
                    )
                ]
            )
            y_offset += 1

    def on_select(self, input):
        self._my_widgets[self.edit_cell[1]][0].value = self._my_widgets[self.selected_row()][0].edit()

    def selected_row(self):
        return self.edit_cell[0]

    def display_value(self, vl):
        # print(vl)
        return int(vl)

    def calculate_area_needed(self):
        return 2, 0


class BoxTitle(npyscreen.BoxTitle):
    _contained_widget = GridColTitles


class KWMainForm(npyscreen.FormBaseNew):
    def __init__(self, *args, config, **kwargs):
        self.config = config

        super().__init__(*args, **kwargs)

    def create(self):
        config = Display(
            vertical_line=self.config["panel_resolution"]["vertical_line"],
            ratio=(self.config["panel_resolution"]["right"]["top"] / self.config["panel_resolution"]["right"][
                "bottom"]),
            usable_space=self.useable_space()
        )()
        # self.box = self.add(Box, values=[Combo(self), Combo(self)], value=1)

        self.box = self.add(GridColTitles, always_show_cursor=True,
            select_whole_line=True)

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)


class KWApplication(npyscreen.NPSAppManaged):
    def __init__(self):
        config = read_config()

        self.meta = config["metadata"]
        self.app_config = config["data"]

        super(KWApplication, self).__init__()

    def main(self):
        self.form = self.addForm(
            f_id="MAIN",
            FormClass=KWMainForm,
            name=f"{self.meta['name']} v{self.meta['version']}",
            config=self.app_config
        )

        self.form.edit()


if __name__ == '__main__':
    try:
        a = KWApplication()
        a.run()
    except KeyboardInterrupt:
        exit(0)

