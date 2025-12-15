from loader import DataLoad

class Enemy:
    def __init__(self, name):
        self.loader = DataLoad()
        self.stats = self.loader.load_e_stats(name)
        self.name = name
        self.dead = False 
        self.turn_count = 0
        self.stun = 0
        self._load_stats()

    def _load_stats(self):
        stats = self.stats
        self.hp = stats.get("hp", 10)
        self.dxt = stats.get("dxt", 5)
        self.str = stats.get("str", 5)
        self.spd = stats.get("spd", 1)
        self.agr = stats.get("agr", 0.5)
        self.vis = stats.get("vis", 1)
        self.spd = stats.get("spd", 1)
        self.atk_spd = stats.get("atk_spd", 1)
        self.c_atk = stats.get("c_atk", 0.0)
        self.dir = stats.get("dir", "rand")

    def update_turn(self):
        self.turn_count += 1
        if self.stun > 0:
            self.stun -= 1

    def take_dmg(self, dmg):
        self.dead = False
        self.hp[0] -= dmg
        if self.hp[0] <= 0:
            self.dead = True
        return self.dead

    def atk(self):
        import random 
        self.attk = self.str[0] + random.randint(-2, 2)
        return self.attk

    def __str__(self):
        return f"{self.name}, HP: {self.hp}, dxt: {self.dxt}, str: {self.str}, agr: {self.agr}, vis: {self.vis}, spd: {self.spd}, atk_spd: {self.atk_spd}, c_atk: {self.c_atk}, dir: {self.dir}"
