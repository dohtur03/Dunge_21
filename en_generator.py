from objects.enemies import Enemy
from loader import DataLoad
import random

def generate_enemies(level, num_enemies=None):
    loader = DataLoad()
    enemy_types = ["zombie", "vampire", "ghost", "ogre", "snake_mage"]
    
    if num_enemies is None:
        base_count = min(3 + (level-1)//3, 12)
        num_enemies = random.randint(max(1, base_count-2), base_count)
    
    enemies = []
    for _ in range(num_enemies):
        enemy_type = random.choice(enemy_types)
        enemy = Enemy(enemy_type, level=level)  
        enemy.x = random.randint(1, 80) 
        enemy.y = random.randint(1, 24)
        enemies.append(enemy)
    
    return enemies

