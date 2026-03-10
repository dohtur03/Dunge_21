class Enemy:
    def __init__(self, name: str, char: str, y: int, x: int, hp: int, strength: int, exp_reward: int):
        self.name = name
        self.char = char  # Символ на экране (например, 'g' для гоблина)
        self.y = y
        self.x = x
        self.hp = hp
        self.max_hp = hp
        self.strength = strength
        self.exp_reward = exp_reward