from dataclasses import dataclass
import requests


@dataclass
class Gitlab:
    api: str
    token: str
