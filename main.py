from en_generator import generate_enemies
from game_state import GameState
from combat_loop import CombatLoop

def main():
    level = 1
    enemies = generate_enemies(level, num_enemies=2)
    
    state = GameState(level, enemies)
    
    combat = CombatLoop(state)
    combat.run()

if __name__ == "__main__":
    main()

