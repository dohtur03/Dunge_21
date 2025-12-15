from loader import DataLoad
import random

class Enemy:
    def __init__(self, name, level):  
        self.loader = DataLoad()
        self.stats = self.loader.load_e_stats(name, level) 
        self.name = self.stats.get("name", "Unknown") 
        self.dead = False
        self.turn_count = 0
        self._load_stats()
        self.x = 0  
        self.y = 0

    def _load_stats(self):
        stats = self.stats
        self.hp = stats.get("hp", 10)
        self.dxt = stats.get("dxt", 5)
        self.str = stats.get("str", 5)   
        self.defense = stats.get("defense", 3)

    def take_dmg(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.dead = True
        return self.dead

    def atk(self, game_state):  # Pass GameState instead of defender
        roll = random.randint(1, 20)
        hero_dxt = game_state.scale_stat(game_state.hero['dxt'], game_state.level)
        if roll + (self.str // 2) < hero_dxt:
            damage = 0
        else:
            hero_def = game_state.scale_stat(game_state.hero['defense'], game_state.level)
            damage = max(1, self.str - hero_def)
            game_state.take_damage(damage)
        return damage
    
    def __str__(self):
        return f"{self.name} HP:{self.hp} STR:{self.str} DXT:{self.dxt} DEF:{self.defense}"

