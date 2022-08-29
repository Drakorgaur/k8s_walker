import npyscreen
from app.config import Filter


class BulkBox(npyscreen.BoxTitle):
    class BulkMultiLine(npyscreen.MultiLine):
        @staticmethod
        def backparse_filters(_filters: dict[str, Filter]):
            values = []
            for key, value in _filters.items():
                _value = value['options'][int(value["selected"])] if value["selected"] not in [None, ''] else None
                values.append(f"{key}: {_value}")
            return values

        def __init__(self, *args, filters: dict[str, Filter], **keywords):
            super(BulkBox.BulkMultiLine, self).__init__(*args, **keywords)
            self.filters = filters
            self.values = self.backparse_filters(filters)

        def update_filters(self):
            self.values = self.backparse_filters(self.filters)
            self.display()

    _contained_widget = BulkMultiLine

    def __init__(self, screen, contained_widget_arguments, *args, **keywords):
        super(BulkBox, self).__init__(screen, contained_widget_arguments=contained_widget_arguments, *args, **keywords)
