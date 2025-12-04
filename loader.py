import json

class DataLoad:
    def __init__(self, data_path="data/"):
        self.data_path = data_path

    def load_enemies(self):
        with open(f"{self.data_path}enemies.json", "r", encoding="utf-8") as file:
            return json.load(file)

    def load_e_stats(self, e_name):
        enemies = self.load_enemies()
        return enemies.get(e_name, {})
