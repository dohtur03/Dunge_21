import json

class DataLoad:
    def __init__(self, data_path="data/"):
        self.data_path = data_path
        self.enemies_data = self.load_enemies()

    def load_enemies(self):
        with open(f"{self.data_path}enemies.json", "r", encoding="utf-8") as file:
            return json.load(file)

    def load_e_stats(self, name, level):
        raw_stats = self.enemies_data[name]
        return {
            "name": raw_stats["name"],
            "hp": self.scale(raw_stats["hp"], level),
            "str": self.scale(raw_stats["str"], level),
            "dxt": self.scale(raw_stats["dxt"], level), 
            "defense": self.scale(raw_stats["defense"], level)
        }

    def scale(self, stat_range, level):
        return stat_range[0] + (level-1) * (stat_range[1] - stat_range[0]) / 20

