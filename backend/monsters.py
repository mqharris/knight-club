# Monster definitions for Knight Club
import random

class Monster:
    def __init__(self, name, hp, attack, defense, agility, xp_reward, gold_drop, loot_table):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.agility = agility
        self.xp_reward = xp_reward
        self.gold_drop = gold_drop  # (min, max) tuple
        self.loot_table = loot_table  # List of (item_id, drop_chance) tuples
    
    def to_dict(self):
        return {
            'name': self.name,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'defense': self.defense,
            'agility': self.agility
        }

# Monster database - organized by difficulty
MONSTERS = {
    'easy': [
        Monster(
            name='Level 1 Slime',
            hp=20,
            attack=8,
            defense=2,
            agility=5,
            xp_reward=10,
            gold_drop=(5, 20),
            loot_table=[
                (101, 0.70),  # 70% Slime Residue
                (201, 0.10),  # 10% Wooden Sword
                (202, 0.10),  # 10% Wooden Shield
                (203, 0.05),  # 5% Wooden Helmet
                (204, 0.05),  # 5% Wooden Chest Armor
            ]
        ),
        Monster(
            name='Giant Rat',
            hp=30,
            attack=10,
            defense=3,
            agility=8,
            xp_reward=15,
            gold_drop=(8, 25),
            loot_table=[
                (101, 0.40),  # 40% Slime Residue
                (201, 0.15),  # 15% Wooden Sword
                (206, 0.10),  # 10% Wooden Bow
                (208, 0.10),  # 10% Wooden Dagger
                (202, 0.10),  # 10% Wooden Shield
            ]
        ),
        Monster(
            name='Weak Goblin',
            hp=35,
            attack=12,
            defense=4,
            agility=6,
            xp_reward=20,
            gold_drop=(10, 30),
            loot_table=[
                (102, 0.80),  # 80% Goblin Ear
                (201, 0.15),  # 15% Wooden Sword
                (207, 0.10),  # 10% Wooden Staff
                (203, 0.08),  # 8% Wooden Helmet
                (204, 0.08),  # 8% Wooden Chest Armor
            ]
        ),
    ],
    'medium': [
        Monster(
            name='Forest Wolf',
            hp=60,
            attack=18,
            defense=6,
            agility=12,
            xp_reward=40,
            gold_drop=(25, 60),
            loot_table=[
                (103, 0.75),  # 75% Wolf Fang
                (301, 0.20),  # 20% Stone Sword
                (302, 0.15),  # 15% Stone Axe
                (303, 0.10),  # 10% Stone Shield
            ]
        ),
        Monster(
            name='Goblin Warrior',
            hp=70,
            attack=20,
            defense=8,
            agility=10,
            xp_reward=50,
            gold_drop=(30, 70),
            loot_table=[
                (102, 0.90),  # 90% Goblin Ear
                (301, 0.25),  # 25% Stone Sword
                (303, 0.20),  # 20% Stone Shield
                (304, 0.15),  # 15% Stone Helmet
                (305, 0.10),  # 10% Stone Chest Armor
            ]
        ),
        Monster(
            name='Troglodite',
            hp=90,
            attack=22,
            defense=12,
            agility=5,
            xp_reward=60,
            gold_drop=(40, 80),
            loot_table=[
                (302, 0.30),  # 30% Stone Axe
                (301, 0.25),  # 25% Stone Sword
                (305, 0.20),  # 20% Stone Chest Armor
                (303, 0.15),  # 15% Stone Shield
            ]
        ),
    ],
    'hard': [
        Monster(
            name='Orc',
            hp=120,
            attack=28,
            defense=15,
            agility=8,
            xp_reward=100,
            gold_drop=(60, 120),
            loot_table=[
                (302, 0.40),  # 40% Stone Axe
                (301, 0.35),  # 35% Stone Sword
                (305, 0.30),  # 30% Stone Chest Armor
                (304, 0.25),  # 25% Stone Helmet
            ]
        ),
    ]
}

def get_monster(difficulty='easy', index=0):
    """
    Get a random monster by difficulty.
    If index is provided and valid, returns that specific monster.
    Otherwise returns a random monster from that difficulty tier.
    """
    monsters = MONSTERS.get(difficulty, MONSTERS['easy'])
    if not monsters:
        return MONSTERS['easy'][0]  # Fallback to easy slime
    
    # If index is specified and valid, use it
    if 0 <= index < len(monsters):
        return monsters[index]
    
    # Otherwise, return a random monster from the tier
    return random.choice(monsters)
