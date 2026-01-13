class Item:
    def __init__(self, name, effect_duration, effect_type, value, description_template):
        self.name = name
        self.effect_duration = effect_duration
        self.effect_type = effect_type
        self.value = value
        self.description_template = description_template
        self.description = description_template.format(value=value, effect_duration=effect_duration)
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.description})"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "effect_duration": self.effect_duration,
            "effect_type": self.effect_type,
            "value": self.value,
            "description_template": self.description_template,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        return cls(**data)

    items = {
        "Weapon": [
            {"name": "Rusty Sword", "effect_duration": 0, "effect_type": "strength", "value": 1, "description_template": "+{value} STR"},
            {"name": "Broken Staff", "effect_duration": 0, "effect_type": "strength", "value": 1, "description_template": "+{value} STR"},
            {"name": "Iron Dagger", "effect_duration": 0, "effect_type": "strength", "value": 2, "description_template": "+{value} STR"},
            {"name": "Bronze Axe", "effect_duration": 0, "effect_type": "strength", "value": 2, "description_template": "+{value} STR"},
            {"name": "Steel Longsword", "effect_duration": 0, "effect_type": "strength", "value": 3, "description_template": "+{value} STR"},
            {"name": "Dual Knives", "effect_duration": 0, "effect_type": "strength", "value": 3, "description_template": "+{value} STR"},
            {"name": "Elven Blade", "effect_duration": 0, "effect_type": "strength", "value": 4, "description_template": "+{value} STR"},
            {"name": "Hammer of Faith", "effect_duration": 0, "effect_type": "strength", "value": 4, "description_template": "+{value} STR"},
            {"name": "Enchanted Blade", "effect_duration": 0, "effect_type": "strength", "value": 5, "description_template": "+{value} STR"},
            {"name": "Paladin's Sword", "effect_duration": 0, "effect_type": "strength", "value": 5, "description_template": "+{value} STR"},
            {"name": "Dragon Slayer", "effect_duration": 0, "effect_type": "strength", "value": 6, "description_template": "+{value} STR"},
            {"name": "Stormbringer", "effect_duration": 0, "effect_type": "strength", "value": 7, "description_template": "+{value} STR"},
        ],
        "Food": [
            {"name": "Golden Apple", "effect_duration": 0, "effect_type": "hits", "value": 2, "description_template": "+{value} HP"},
            {"name": "Forest Mushroom", "effect_duration": 0, "effect_type": "hits", "value": 2, "description_template": "+{value} HP"},
            {"name": "Raw Meat", "effect_duration": 0, "effect_type": "hits", "value": 4, "description_template": "+{value} HP"},
            {"name": "Watermelon", "effect_duration": 0, "effect_type": "hits", "value": 4, "description_template": "+{value} HP"},
            {"name": "Brown Ale", "effect_duration": 0, "effect_type": "hits", "value": 5, "description_template": "+{value} HP"},
            {"name": "Bread", "effect_duration": 0, "effect_type": "hits", "value": 5, "description_template": "+{value} HP"},
            {"name": "Healing Leaves", "effect_duration": 0, "effect_type": "hits", "value": 6, "description_template": "+{value} HP"},
            {"name": "Cheese", "effect_duration": 0, "effect_type": "hits", "value": 6, "description_template": "+{value} HP"},
            {"name": "Mystic Berry", "effect_duration": 0, "effect_type": "hits", "value": 8, "description_template": "+{value} HP"},
            {"name": "Roasted Turkey", "effect_duration": 0, "effect_type": "hits", "value": 10, "description_template": "+{value} HP"},
            {"name": "Boar Meat Steak", "effect_duration": 0, "effect_type": "hits", "value": 12, "description_template": "+{value} HP"},
            {"name": "Ambrosia", "effect_duration": 0, "effect_type": "hits", "value": 15, "description_template": "+{value} HP"},
        ],
        "Potion": [
            {"name": "Weak Health Potion", "effect_duration": 1, "effect_type": "max_hits", "value": 5, "description_template": "+{value} MAX HP for {effect_duration} min"},
            {"name": "Health Potion", "effect_duration": 1, "effect_type": "max_hits", "value": 10, "description_template": "+{value} MAX HP for {effect_duration} min"},
            {"name": "Strong Health Potion", "effect_duration": 1, "effect_type": "max_hits", "value": 15, "description_template": "+{value} MAX HP for {effect_duration} min"},
            {"name": "Great Health Potion", "effect_duration": 1, "effect_type": "max_hits", "value": 20, "description_template": "+{value} MAX HP for {effect_duration} min"},
            {"name": "Weak Agility Potion", "effect_duration": 1, "effect_type": "agility", "value": 2, "description_template": "+{value} MAX AGI for {effect_duration} min"},
            {"name": "Agility Potion", "effect_duration": 1, "effect_type": "agility", "value": 4, "description_template": "+{value} MAX AGI for {effect_duration} min"},
            {"name": "Strong Agility Potion", "effect_duration": 1, "effect_type": "agility", "value": 8, "description_template": "+{value} MAX AGI for {effect_duration} min"},
            {"name": "Great Agility Potion", "effect_duration": 1, "effect_type": "agility", "value": 10, "description_template": "+{value} MAX AGI for {effect_duration} min"},
            {"name": "Weak Strength Potion", "effect_duration": 1, "effect_type": "strength", "value": 2, "description_template": "+{value} MAX STR for {effect_duration} min"},
            {"name": "Strength Potion", "effect_duration": 1, "effect_type": "strength", "value": 4, "description_template": "+{value} MAX STR for {effect_duration} min"},
            {"name": "Strong Strength Potion", "effect_duration": 1, "effect_type": "strength", "value": 8, "description_template": "+{value} MAX STR for {effect_duration} min"},
            {"name": "Great Strength Potion", "effect_duration": 1, "effect_type": "strength", "value": 10, "description_template": "+{value} MAX STR for {effect_duration} min"},
        ],
        "Scroll": [
            {"name": "Weak Scroll of Health", "effect_duration": 0, "effect_type": "max_hits", "value": 2, "description_template": "+{value} MAX HP"},
            {"name": "Scroll of Health", "effect_duration": 0, "effect_type": "max_hits", "value": 4, "description_template": "+{value} MAX HP"},
            {"name": "Strong Scroll of Health", "effect_duration": 0, "effect_type": "max_hits", "value": 6, "description_template": "+{value} MAX HP"},
            {"name": "Great Scroll of Health", "effect_duration": 0, "effect_type": "max_hits", "value": 8, "description_template": "+{value} MAX HP"},
            {"name": "Weak Scroll of Agility", "effect_duration": 0, "effect_type": "agility", "value": 1, "description_template": "+{value} MAX AGI"},
            {"name": "Scroll of Agility", "effect_duration": 0, "effect_type": "agility", "value": 2, "description_template": "+{value} MAX AGI"},
            {"name": "Strong Scroll of Agility", "effect_duration": 0, "effect_type": "agility", "value": 3, "description_template": "+{value} MAX AGI"},
            {"name": "Great Scroll of Agility", "effect_duration": 0, "effect_type": "agility", "value": 4, "description_template": "+{value} MAX AGI"},
            {"name": "Weak Scroll of Strength", "effect_duration": 0, "effect_type": "strength", "value": 1, "description_template": "+{value} MAX STR"},
            {"name": "Scroll of Strength", "effect_duration": 0, "effect_type": "strength", "value": 2, "description_template": "+{value} MAX STR"},
            {"name": "Strong Scroll of Strength", "effect_duration": 0, "effect_type": "strength", "value": 3, "description_template": "+{value} MAX STR"},
            {"name": "Great Scroll of Strength", "effect_duration": 0, "effect_type": "strength", "value": 4, "description_template": "+{value} MAX STR"},
        ]
    }