import os
import json
from typing import Optional, TypedDict, ClassVar, Union, TypeVar

import npyscreen.wgwidget

DEFAULT_CONFIG_PATH = f"{os.path.expanduser('~')}/.local/share/k8s_walker"
DEFAULT_CONFIG = {}


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


Filter = TypedDict("Filter", {"selected": Union[int, None], "options": list[str]})


class __Panel:
    __PanelRight = TypedDict("__PanelRight", {"top": int, "bottom": int, "left": int})
    PanelResolution = TypedDict("PanelResolution", {"vertical_line": float, "right": __PanelRight})


Config = TypedDict("Config", {"filters": dict[str, Filter], "panel_resolution": __Panel.PanelResolution}, total=False)

Widget = TypeVar("Widget", bound=npyscreen.wgwidget.Widget)


def seed_config() -> str or None:
    if os.access(os.path.split(DEFAULT_CONFIG_PATH)[-1], os.W_OK | os.R_OK):
        with open(os.path.join(DEFAULT_CONFIG_PATH, 'config.json'), 'w') as config_file:
            json.dump(DEFAULT_CONFIG, config_file)
            return DEFAULT_CONFIG_PATH
    return None


def find_config(arg: Optional[str] = None) -> str:
    """Find the config file in the current directory and return the path to it."""

    def config_in_dir(dir_path: str) -> str or None:
        if not isinstance(dir_path, str):
            return None
        root, _, files = next(os.walk(dir_path))
        if 'config.json' in files:
            return os.path.join(root, 'config.json')

    possible_locations = [arg, DEFAULT_CONFIG_PATH, os.getcwd()]

    for location in possible_locations:
        try:
            if config_path := config_in_dir(location):
                return config_path
        except StopIteration:
            continue

    raise FileNotFoundError("No config.json found")


def read_config(config_path: str or None = None) -> dict:
    if config_path is None:
        config_path = find_config()
    with open(config_path, 'r') as config_file:
        return json.load(config_file)
