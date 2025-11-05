# Monster definitions for Knight Club

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
            gold_drop=(5, 20),  # Drops 5-20 gold
            loot_table=[
                (101, 0.70),  # 70% Slime Residue
                (201, 0.10),  # 10% Wooden Sword
                (202, 0.10),  # 10% Wooden Shield
                (203, 0.05),  # 5% Wooden Helmet
                (204, 0.05),  # 5% Wooden Chest Armor
            ]
        )
    ],
    'medium': [
        # To be added later
    ],
    'hard': [
        # To be added later
    ]
}

def get_monster(difficulty='easy', index=0):
    """
    Get a monster by difficulty and index.
    For now, just returns the first (and only) monster in each tier.
    Later can be expanded to random selection.
    """
    monsters = MONSTERS.get(difficulty, MONSTERS['easy'])
    if not monsters:
        return MONSTERS['easy'][0]  # Fallback to easy slime
    return monsters[min(index, len(monsters) - 1)]
