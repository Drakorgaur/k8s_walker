import curses

import npyscreen
from _typing import Filter


class Multi(npyscreen.TitleCombo):
    def edit(self):
        self.editing = True
        self.display()
        self.entry_widget.edit()
        self.how_exited = self.entry_widget.how_exited
        self.editing = False
        self.display()
        return self.entry_widget.value


class Grid(npyscreen.SimpleGrid):
    _contained_widgets = Multi
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
        if column_width < 1: raise Exception("Too many columns for space available")
        h_coord = 0
        for name, values in self.contained_widget_value.items():
            self._my_widgets.append([self._contained_widgets(self.parent, rely=h_coord + self.rely,
                                                   relx=self.relx + self.additional_x_offset,
                                                   width=column_width, height=self.row_height,  name=name, values=values["options"])])
            h_coord += 1

    def display_value(self, vl):
        return int(vl) if vl != "" else None

    def calculate_area_needed(self):
        return len(self.contained_widget_value), 0

    def on_select(self, input):
        value = self._my_widgets[self.edit_cell[0]][0].edit()
        self.values[self.edit_cell[0]][self.edit_cell[1]] = value

    def key_up(self, event):
        self.h_move_line_up(event)
        self.h_move_line_up(event)

    def key_down(self, event):
        self.h_move_line_down(event)
        self.h_move_line_down(event)

    def set_up_handlers(self):
        self.handlers = {
                    curses.KEY_UP:      self.key_up,
                    curses.KEY_DOWN:    self.key_down,
                    curses.KEY_HOME:    self.h_show_beginning,
                    curses.KEY_END:     self.h_show_end,
                    curses.ascii.TAB:   self.h_exit,
                    curses.ascii.ESC:   self.h_exit,
                    curses.KEY_MOUSE:    self.h_exit_mouse,
                }

        self.complex_handlers = [
                    ]
        self.parent.set_up_handlers()


class Box(npyscreen.BoxTitle):
    name = "filters"
    _contained_widget = Grid

    def __init__(self, screen, contained_widget_arguments=None, *args, **keywords):
        super(Box, self).__init__(screen, contained_widget_arguments=contained_widget_arguments, *args, **keywords)

    def set_up_handlers(self):
        self.handlers = {}