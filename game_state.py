import json
import os

class GameState:
    def __init__(self, level, enemies, data_path="data/"):
        self.data_path = data_path
        self.level = level
        self.enemies = enemies 
        os.makedirs(self.data_path, exist_ok=True)
        self.hero = self._load_hero()
        self.hero_current_hp = self.scale_stat(self.hero['hp'], level)

    def take_damage(self, dmg):
        self.hero_current_hp -= dmg
        if self.hero_current_hp < 0:
            self.hero_current_hp = 0

    def _load_hero(self):
        hero_path = f"{self.data_path}hero.json"
        with open(hero_path, 'r') as f:
            data = json.load(f)["hero"]
        return data
    
    def _load_level(self):
        level_path = f"{self.data_path}level.json"
        try:
            with open(level_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"current_level": self.level, "map_size": [80, 24]}
    
    def scale_stat(self, stat_range, level):
        return stat_range[0] + (level-1) * (stat_range[1] - stat_range[0]) / 20
    
    def save_session(self, filename="session.json"):
        session_path = f"{self.data_path}{filename}"
        session = {
            'level': self.level,
            'hero_hp': self.hero_current_hp,
            'enemies': [{'name': e.name, 'hp': e.hp, 'x': e.x, 'y': e.y, 'dead': getattr(e, 'dead', False)} for e in self.enemies]
        }
        with open(session_path, 'w') as f:
            json.dump(session, f, indent=4)

