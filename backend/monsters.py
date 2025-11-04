# Monster definitions for Knight Club

class Monster:
    def __init__(self, name, hp, attack, defense, agility, xp_reward):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.agility = agility
        self.xp_reward = xp_reward
    
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
            xp_reward=10
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
