# Item definitions for Knight Club

ITEMS = {
    # Materials (stackable)
    101: {
        "name": "Slime Residue",
        "type": "material",
        "stackable": True,
        "description": "Gooey residue (Not Kombucha)",
        "rarity": "common"
    },
    
    # Wooden Equipment (non-stackable, level 1-10 drops)
    201: {
        "name": "Wooden Sword",
        "type": "weapon",
        "stackable": False,
        "slot": "weapon",
        "stats": {"attack": 5},
        "description": "A basic wooden sword (Actually just a stick)",
        "rarity": "uncommon"
    },
    202: {
        "name": "Wooden Shield",
        "type": "armor",
        "stackable": False,
        "slot": "shield",
        "stats": {"defense": 3},
        "description": "A simple wooden shield. (looks fragile, is fragile)",
        "rarity": "uncommon"
    },
    203: {
        "name": "Wooden Helmet",
        "type": "armor",
        "stackable": False,
        "slot": "helm",
        "stats": {"defense": 2},
        "description": "A crude wooden helmet (splinters included)",
        "rarity": "uncommon"
    },
    204: {
        "name": "Wooden Chest Armor",
        "type": "armor",
        "stackable": False,
        "slot": "chest",
        "stats": {"defense": 4},
        "description": "Wooden planks strapped together as armor (step aside macgyver)",
        "rarity": "uncommon"
    },
}

def get_item(item_id):
    """Get item definition by ID."""
    return ITEMS.get(item_id)

def get_items_by_type(item_type):
    """Get all items of a specific type."""
    return {k: v for k, v in ITEMS.items() if v['type'] == item_type}
