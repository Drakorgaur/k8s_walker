import npyscreen

from _typing import Filter


class FiltersPreview(npyscreen.BoxTitle):
    name = "Filters"
    _contained_widget = npyscreen.MultiLine

    def __init__(self, screen, filters: dict = None, *args, **keywords):
        def interpret_dict(f: dict[str, Filter]) -> list[str]:
            def set_space(s: str) -> str:
                return f"{25 - len(s)}"
            return [f"{_filter}{':' : <{set_space(_filter)}}{value['selected']}" for _filter, value in f.items()]
        super(FiltersPreview, self).__init__(
            screen,
            contained_widget_arguments={"name": "asdasdads", "values": interpret_dict(filters)},
            *args,
            **keywords
        )


class FilterForm(npyscreen.FormBaseNew):
    def create(self):
        self.filters = self.add(npyscreen.BoxTitle, name="filters")