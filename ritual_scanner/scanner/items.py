import re


def get_item_class(item_data: str) -> str | None:
    if m := re.search(r"^Item Class: ([\w\s]+)$", item_data, re.MULTILINE):
        return m.group(1)


def get_item_dimensions(item_class: str) -> tuple[int, int]:
    # width, height
    if item_class in (
        "Helmets",
        "Delve Stackable Socketable Currency",
        "Claws",
        "Gloves",
    ):
        return (2, 2)

    if item_class == "Two Hand Axes":
        return (2, 4)

    if item_class == "Body Armours":
        return (2, 3)

    if item_class == "Daggers":
        return (1, 3)

    return (1, 1)
