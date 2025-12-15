import random

class CombatLoop:
    def __init__(self, state):
        self.state = state
    
    def run(self):
        print(f"\n=== COMBAT LVL: {self.state.level} ===")
        
        while self.state.hero_current_hp > 0 and any(not e.dead for e in self.state.enemies):
            self.wait_for_input()
            self.hero_attack()
            self.enemies_attack()
            self.print_status()
        
        self.end_combat()
    
    def wait_for_input(self):
        print("\nPress ENTER to attack nearest enemy...")
        input()  
    
    def hero_attack(self):
        target = next((e for e in self.state.enemies if not e.dead), None)
        if not target:
            print("No alive enemies!")
            return
        
        hero_str = self.state.scale_stat(self.state.hero['str'], self.state.level)
        roll = random.randint(1, 20)
        to_hit = roll + (hero_str // 2)
    
        if to_hit >= target.dxt:
            dmg = max(1, int(hero_str - target.defense))
            target.take_dmg(dmg)
            print(f"Hero hits {target.name} for {dmg}!")
        else:
               print(f"Hero misses {target.name}! (roll {roll} + {hero_str//2} = {to_hit} vs {target.dxt})")

    def enemies_attack(self):
        for enemy in self.state.enemies:
            if not enemy.dead:
                dmg = enemy.atk(self.state)  
                if dmg > 0:
                    print(f"{enemy.name} hits for {dmg}!")
 
    def print_status(self):
        print(f"\nHero HP: {self.state.hero_current_hp}")
        for e in self.state.enemies:
            print(f"{e.name}: {max(0, e.hp)}HP {'💀' if e.dead else ''}")
        self.state.save_session()
    
    def end_combat(self):
        print("Victory!" if all(e.dead for e in self.state.enemies) else "Defeat!")
        self.state.save_session()

