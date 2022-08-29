import curses
import npyscreen

from app.config import Filter
from app.event import Event


class TestComboBox(npyscreen.ComboBox, Event):
    def set_up_handlers(self):
        super(TestComboBox, self).set_up_handlers()

        self.handlers[curses.KEY_DOWN] = self.key_down
        self.handlers[curses.KEY_UP] = self.key_up

    def key_down(self, inpt):
        self.event("onCellDown")
        self.h_exit_escape(inpt)

    def key_up(self, inpt):
        self.h_exit_up(inpt)
        self.event("onCellUp")
        self.h_exit_escape(inpt)


class TestTitleCombo(npyscreen.TitleCombo):
    _entry_type = TestComboBox

    def edit(self):
        self.editing = True
        self.display()
        wg: TestComboBox = self.entry_widget
        wg.edit()
        self.how_exited = wg.how_exited
        self.editing = False
        self.display()

        return wg.value


class Grid(npyscreen.SimpleGrid, Event):
    _contained_widgets = TestTitleCombo
    default_column_number = 1

    def __init__(self, screen, *args, filters: dict[str, Filter], **keywords):
        self.contained_widget_value = filters
        super(Grid, self).__init__(screen, *args, **keywords)

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
        h_coord = 0
        for name, values in self.contained_widget_value.items():
            self._my_widgets.append(
                [
                    self._contained_widgets(
                        self.parent,
                        rely=h_coord + self.rely,
                        relx=self.relx + self.additional_x_offset,
                        width=column_width,
                        height=self.row_height,
                        name=name,
                        values=values["options"]    # changed
                    )
                ]
            )
            h_coord += 1

    def display_value(self, vl):
        return int(vl) if vl != "" else None

    def calculate_area_needed(self):
        return len(self.contained_widget_value), 0

    def get_selected_widget(self) -> TestTitleCombo:
        return self._my_widgets[self.edit_cell[0]][0]

    def on_select(self, input):
        wg: TestTitleCombo = self.get_selected_widget()
        value = wg.edit()
        self.values[self.edit_cell[0]][self.edit_cell[1]] = value
        self.editing = False
        self.contained_widget_value[wg.name]["selected"] = value


class Box(npyscreen.BoxTitle, Event):
    name = "filters"
    _contained_widget = Grid

    def __init__(self, screen, contained_widget_arguments=None, *args, **keywords):
        self.how_exited = 1
        super(Box, self).__init__(screen, contained_widget_arguments=contained_widget_arguments, *args, **keywords)

    def set_up_handlers(self):
        super(Box, self).set_up_handlers()

