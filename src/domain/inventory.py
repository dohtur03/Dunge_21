from domain.item import Item


class Inventory:
    def __init__(self, player_name: str, game):
        self.player_name = player_name
        self.game = game
        self.categories = ["Weapon", "Food", "Potion", "Scroll", "Back"]
        self.category_items = {
            "Weapon": [None] * 9,
            "Food": [None] * 9,
            "Potion": [None] * 9,
            "Scroll": [None] * 9,
        }

    def to_dict(self) -> dict:
        result = {}
        for category, items in self.category_items.items():
            result[category] = [
                item.to_dict() if item is not None else None
                for item in items
            ]
        return result

    @classmethod
    def from_dict(cls, player_name, game, data: dict) -> "Inventory":
        inv = cls(player_name, game)
        for category, item_list in data.items():
            if category in inv.category_items:
                inv.category_items[category] = [
                    Item.from_dict(item_data) if item_data is not None else None
                    for item_data in item_list
                ]
        return inv