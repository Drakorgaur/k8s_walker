import npyscreen
from .config import read_config
from .forms import KWMainForm


class KWApplication(npyscreen.StandardApp):
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
        config = read_config()

        self.meta = config["metadata"]
        self.app_config = config["data"]

        super(KWApplication, self).__init__()

    def onStart(self):
        # Events
        self.add_event_hander("onCellUp", self.on_cell_up)
        self.add_event_hander("onCellDown", self.on_cell_down)
        self.add_event_hander("onFilterChange", self.on_filter_change)

        # Forms
        self.main = self.addForm(
            f_id="MAIN",
            FormClass=KWMainForm,
            name=f"{self.meta['name']} v{self.meta['version']}",
            config=self.app_config
        )

    def __grid(self):
        return self.main.filters._my_widgets[0]

    def on_cell_up(self, event):
        self.__grid().h_move_line_up(event)

    def on_cell_down(self, event):
        self.__grid().h_move_line_down(event)

    def on_filter_change(self, event):
        # TODO: TBD
        self.main.bulk._my_widgets[0].update_filters()
