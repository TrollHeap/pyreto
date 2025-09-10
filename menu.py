from enum import Enum


class MenuChoice(Enum):
    COURSE = 1
    CHEATSHEET = 2
    EXERCISES = 3
    PRACTICE = 4
    TOPICS = 5
    SCHEDULE = 6
    QUIT = 7


def parse_menu_choice(raw: str) -> MenuChoice:
    try:
        return MenuChoice(int(raw))
    except Exception:
        return MenuChoice.QUIT
