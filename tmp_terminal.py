#!/usr/bin/python3.9
from curses import ascii

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


class FixedText(npyscreen.TitleFixedText):
    name = "FixedText"


class TitleCombo(npyscreen.ComboBox):
    name = "Some"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.values = ["1, 2", "2,4"]


class GridColTitles(npyscreen.SimpleGrid):
    _contained_widgets = TitleCombo
    values = []

    def make_contained_widgets(self):
        if self.column_width_requested:
            # don't need a margin for the final column
            self.columns = (self.width + self.col_margin) // (self.column_width_requested + self.col_margin)
        elif self.columns_requested:
            self.columns = self.columns_requested
        else:
            self.columns = self.default_column_number
        self._my_widgets = []
        column_width = (self.width + self.col_margin - self.additional_x_offset) // self.columns
        column_width -= self.col_margin
        self._column_width = column_width
        if column_width < 1:
            raise Exception("Too many columns for space available")
        y_offset = 0
        for col in range(len(self.values) + 1):
            self._my_widgets.append(
                [
                    self._contained_widgets(
                        self.parent, rely=self.rely + y_offset + self.additional_y_offset,
                        relx=self.relx + self.additional_x_offset, width=column_width,
                        height=self.row_height
                    )
                ]
            )
            y_offset += 1

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            columns=1,
            always_show_cursor=True,
            select_whole_line=True,
            values=[[TitleCombo, TitleCombo], [TitleCombo, TitleCombo]],
            **kwargs
        )


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

        self.something = ""
        self.box = self.add(BoxTitle, name="Right Top",
                            **config["right"]["top"])
        self.box.entry_widget.add_handlers({ascii.NL: self.do_stuff})

        self.add(npyscreen.BoxTitle, name="Right Bottom", values=["first line", "second line"],
                 **config["right"]["bottom"])
        self.b = self.add(npyscreen.BoxTitle, name="Bottom", values=[self.something],
                          **config["left"])

    def quit(self, *args, **kwargs):
        self.parentApp.switchForm(None)

    def do_stuff(self, *args):
        box: BoxTitle = self.box
        self.grid: GridColTitles = self.box.entry_widget
        self.grid._my_widgets[self.grid.edit_cell[0]][0].edit()


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
    a: KWApplication = None
    try:
        a = KWApplication()
        a.run()
    except KeyboardInterrupt:
        print(a.form.box.entry_widget.values)
        exit(0)
