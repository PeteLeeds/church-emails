import json
from typing import List

from events import Event


class Section:
    title: str
    displayTitle: bool
    default: bool
    filters: List[str]
    events: List[Event]

    def __init__(self, section_json: dict) -> None:
        self.title = section_json["title"]
        self.displayTitle = section_json["displayTitle"]
        self.default = section_json["default"]
        self.events = []
        if not self.default:
            self.filters = section_json["filters"]

    def matches_event(self, event: Event) -> bool:
        if self.default:
            return True
        for filter in self.filters:
            if filter.upper() in event.description.upper():
                return True
        return False

    def add_event(self, event: Event) -> None:
        self.events.append(event)

    def create_section_email(self) -> str:
        email_string = f"<h2>{self.title}</h2>" if self.displayTitle else ""
        for event in self.events:
            email_string += event.format_for_email()
        return email_string


def get_sections() -> List[Section]:
    try:
        with open("sections.json") as f:
            sections_json_array = json.load(f)
            return [Section(section_json) for section_json in sections_json_array]
    except:
        default_section = {
            "title": "Default",
            "displayTitle": False,
            "default": True,
        }
        return [Section(default_section)]


def populate_section_events(sections: List[Section], events: List[Event]) -> None:
    for event in events:
        for section in sections:
            if section.matches_event(event):
                section.add_event(event)
                break
