from ritual_scanner.scanner import items


def test_get_item_class():
    item_class = items.get_item_class("""Item Class: Stackable Currency
Rarity: Currency
Blacksmith's Whetstone
--------
Stack Size: 6/20
--------
Improves the quality of a weapon
--------
Right click this item then left click a weapon to apply it. Has greater effect on lower-rarity weapons. The maximum quality is 20%.
Shift click to unstack.
""")

    assert item_class == "Stackable Currency"
