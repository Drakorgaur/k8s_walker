#!/usr/bin/python3.9
import collections

import npyscreen


class Form(npyscreen.FormBaseNew):
    class TextMultiLine(npyscreen.TitleCombo):
        def __init__(
                self, screen,
                begin_entry_at=16,
                field_width=None,
                value=None,
                use_two_lines=None,
                hidden=False,
                labelColor='LABEL',
                allow_override_begin_entry_at=True,
                **keywords):
            super().__init__(
                screen, begin_entry_at, field_width, value, use_two_lines,
                hidden, labelColor, allow_override_begin_entry_at, **keywords
            )
            self.name = "name"
            self.values=["1","2","3"]

            self.add_handlers(
                {
                    "^A": self.on_edit,
                }
            )

        def on_edit(self, input):
            self.parent.parentApp.queue_event(npyscreen.Event("onFiltersChange"))

    def create(self):
        self.add(
            self.TextMultiLine,
            name="Mark",
            values=["Hello", "World"],
        )




class App(npyscreen.StandardApp):
    class NPSEventQueue(npyscreen.apNPSApplicationEvents.NPSEventQueue):
        def get(self, maximum=None):
            if maximum is None:
                maximum = -1
            counter = 1
            while counter != maximum:
                try:
                    yield self.interal_queue.pop()
                except IndexError:
                    pass
                counter += 1

    MAINQUEUE_TYPE = NPSEventQueue

    def __init__(self):
        super(App, self).__init__()
        self.add_event_hander("onFiltersChange", self.on_filter_chnage)

    def onStart(self):
        self.addForm("MAIN", Form)

    def on_filter_chnage(self, event):
        print("BulkBulkBulkBulkBulkBulkBulkBulkBulkBulkBulkBulkBulkBulkBulkBulkBulkBulkBulk")


if __name__ == '__main__':
    T = App()
    T.run()
