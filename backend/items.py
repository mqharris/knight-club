# Item definitions for Knight Club

ITEMS = {
    # Materials (stackable)
    101: {
        "name": "Slime Residue",
        "type": "material",
        "stackable": True,
        # "description": "Gooey residue (Not Kombucha)",
        "rarity": "common"
    },
    
    # Wooden Equipment (non-stackable, level 1-10 drops)
    201: {
        "name": "Wooden Sword",
        "type": "weapon",
        "stackable": False,
        "slot": "weapon",
        "stats": {"attack": 5},
        # "description": "A basic wooden sword (Actually just a stick)",
        "rarity": "uncommon"
    },
    202: {
        "name": "Wooden Shield",
        "type": "armor",
        "stackable": False,
        "slot": "shield",
        "stats": {"defense": 3},
        # "description": "A simple wooden shield. (looks fragile, is fragile)",
        "rarity": "uncommon"
    },
    203: {
        "name": "Wooden Helmet",
        "type": "armor",
        "stackable": False,
        "slot": "helm",
        "stats": {"defense": 2},
        # "description": "A crude wooden helmet (splinters included)",
        "rarity": "uncommon"
    },
    204: {
        "name": "Wooden Chest Armor",
        "type": "armor",
        "stackable": False,
        "slot": "chest",
        "stats": {"defense": 4},
        # "description": "Wooden planks strapped together as armor (step aside macgyver)",
        "rarity": "uncommon"
    },
    205: {
        "name": "Wooden Pants",
        "type": "armor",
        "stackable": False,
        "slot": "pants",
        "stats": {"defense": 3},
        # "description": "Wooden leg armor (what? you want me to stand inside this wooden box?)",
        "rarity": "uncommon"
    },
    206: {
        "name": "Wooden Bow",
        "type": "weapon",
        "stackable": False,
        "slot": "weapon",
        "stats": {"attack": 4, "agility": 2},
        # "description": "A crude wooden bow (arrows sold separately)",
        "rarity": "uncommon"
    },
    207: {
        "name": "Wooden Staff",
        "type": "weapon",
        "stackable": False,
        "slot": "weapon",
        "stats": {"attack": 3, "defense": 2},
        # "description": "A sturdy walking staff (bonk)",
        "rarity": "uncommon"
    },
    208: {
        "name": "Wooden Dagger",
        "type": "weapon",
        "stackable": False,
        "slot": "weapon",
        "stats": {"attack": 3, "agility": 3},
        # "description": "A small wooden blade (one single big single sliver)",
        "rarity": "uncommon"
    },
    
    # Stone Equipment (level 10-20 drops)
    301: {
        "name": "Stone Sword",
        "type": "weapon",
        "stackable": False,
        "slot": "weapon",
        "stats": {"attack": 10},
        # "description": "A heavy stone blade (your enemies will feel the weight)",
        "rarity": "rare"
    },
    302: {
        "name": "Stone Axe",
        "type": "weapon",
        "stackable": False,
        "slot": "weapon",
        "stats": {"attack": 12, "defense": -2},
        # "description": "A brutal stone axe (its a rock)",
        "rarity": "rare"
    },
    303: {
        "name": "Stone Shield",
        "type": "armor",
        "stackable": False,
        "slot": "shield",
        "stats": {"defense": 7, "agility": -1},
        # "description": "A solid stone shield (heavy)",
        "rarity": "rare"
    },
    304: {
        "name": "Stone Helmet",
        "type": "armor",
        "stackable": False,
        "slot": "helm",
        "stats": {"defense": 5, "agility": -1},
        # "description": "A stone helmet (you're balancing a rock on your head)",
        "rarity": "rare"
    },
    305: {
        "name": "Stone Chest Armor",
        "type": "armor",
        "stackable": False,
        "slot": "chest",
        "stats": {"defense": 8, "agility": -2},
        # "description": "Stone plates protecting your vital organs (not chiropractor recommended)",
        "rarity": "rare"
    },
    
    # Iron Equipment (level 20-30 drops)
    401: {
        "name": "Iron Sword",
        "type": "weapon",
        "stackable": False,
        "slot": "weapon",
        "stats": {"attack": 18},
        # "description": "A well-forged iron blade (you called this well forged?)",
        "rarity": "epic"
    },
    402: {
        "name": "Iron Axe",
        "type": "weapon",
        "stackable": False,
        "slot": "weapon",
        "stats": {"attack": 20, "defense": -1},
        # "description": "A brutal iron axe (blunt as)",
        "rarity": "epic"
    },
    403: {
        "name": "Iron Shield",
        "type": "armor",
        "stackable": False,
        "slot": "shield",
        "stats": {"defense": 12, "agility": -2},
        # "description": "A sturdy iron shield (built to last (thats what she said))",
        "rarity": "epic"
    },
    404: {
        "name": "Iron Helmet",
        "type": "armor",
        "stackable": False,
        "slot": "helm",
        "stats": {"defense": 9},
        # "description": "An iron helmet (proper head protection(thats what she said))",
        "rarity": "epic"
    },
    405: {
        "name": "Iron Chest Armor",
        "type": "armor",
        "stackable": False,
        "slot": "chest",
        "stats": {"defense": 14, "agility": -2},
        # "description": "Iron plates forged into proper armor (you've played rpgs before)",
        "rarity": "epic"
    },
    406: {
        "name": "Iron Pants",
        "type": "armor",
        "stackable": False,
        "slot": "pants",
        "stats": {"defense": 10, "agility": -2},
        # "description": "Iron leg armor (left clank right clank left clank...)",
        "rarity": "epic"
    },
    410: {
        "name": "Silk Cape",
        "type": "armor",
        "stackable": False,
        "slot": "cape",
        "stats": {"defense": 2, "agility": 2},
        # "description": "A lightweight cape made of spider silk (surprisingly stylish)",
        "rarity": "epic"
    },
    
    # Materials
    102: {
        "name": "Goblin Ear",
        "type": "material",
        "stackable": True,
        # "description": "A goblin's ear (eww, but valuable)",
        "rarity": "common"
    },
    103: {
        "name": "Wolf Fang",
        "type": "material",
        "stackable": True,
        # "description": "A sharp wolf fang (could make a nice necklace)",
        "rarity": "common"
    },
    104: {
        "name": "Orc Tusk",
        "type": "material",
        "stackable": True,
        # "description": "A massive orc tusk (worth a fortune)",
        "rarity": "rare"
    },
    105: {
        "name": "Spider Silk",
        "type": "material",
        "stackable": True,
        # "description": "Fine silk from a giant spider (lightweight and strong)",
        "rarity": "rare"
    },
    
    # Consumables
    501: {
        "name": "HP Potion",
        "type": "consumable",
        "stackable": True,
        # "description": "Restores 25 HP when consumed",
        "rarity": "common",
        "effect": {"type": "heal", "amount": 25}
    },
}

def get_item(item_id):
    """Get item definition by ID."""
    return ITEMS.get(item_id)

def get_items_by_type(item_type):
    """Get all items of a specific type."""
    return {k: v for k, v in ITEMS.items() if v['type'] == item_type}
