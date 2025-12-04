from objects.enemies import Enemy
from loader import DataLoad

def main():
    loader = DataLoad()

    zomb = Enemy("zombie")
    vamp = Enemy("vampire")
    ghost = Enemy("ghost")
    ogre = Enemy("ogre")
    snake = Enemy("snake_mage")

    print(zomb)
    print(vamp)
    print(ghost)
    print(ogre)
    print(snake)

    zomb.take_dmg(10)
    p_dmg = zomb.atk()
    print(f"zombie attacks: {p_dmg} damage")
    print(zomb)

if __name__ == "__main__":
    main()
