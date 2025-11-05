# Battle system for Knight Club

class Combatant:
    def __init__(self, name, hp, max_hp, attack, defense, agility):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.agility = agility
        self.is_alive = True
    
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        return self.hp
    
    def calculate_damage(self, target):
        """Calculate damage dealt to target"""
        raw_damage = self.attack - target.defense
        return max(1, raw_damage)  # Minimum 1 damage

def simulate_battle(knight_data, monster):
    """
    Simulate a turn-based battle between knight and monster.
    Returns battle log and final knight HP.
    """
    # Create combatants
    knight = Combatant(
        name=knight_data['name'],
        hp=knight_data['current_hp'],
        max_hp=knight_data['max_hp'],
        attack=10 + knight_data.get('attack_bonus', 0),  # Base 10 + equipment
        defense=10 + knight_data.get('defense_bonus', 0),   # Base 10 + equipment
        agility=10 + knight_data.get('agility_bonus', 0)    # Base 10 + equipment
    )
    
    monster_combatant = Combatant(
        name=monster.name,
        hp=monster.hp,
        max_hp=monster.max_hp,
        attack=monster.attack,
        defense=monster.defense,
        agility=monster.agility
    )
    
    battle_log = []
    battle_log.append(f"⚔️ {knight.name} encounters a {monster_combatant.name}!")
    battle_log.append(f"Knight HP: {knight.hp}/{knight.max_hp} | Monster HP: {monster_combatant.hp}/{monster_combatant.max_hp}")
    battle_log.append("")
    
    # Determine turn order based on agility
    if knight.agility >= monster_combatant.agility:
        first = knight
        second = monster_combatant
    else:
        first = monster_combatant
        second = knight
    
    battle_log.append(f"🏃 {first.name} moves first! (Agility: {first.agility})")
    battle_log.append("")
    
    turn = 1
    while knight.is_alive and monster_combatant.is_alive:
        battle_log.append(f"--- Turn {turn} ---")
        
        # First attacker
        damage = first.calculate_damage(second)
        second.take_damage(damage)
        battle_log.append(f"💥 {first.name} attacks {second.name} for {damage} damage!")
        battle_log.append(f"   {second.name} HP: {second.hp}/{second.max_hp}")
        
        if not second.is_alive:
            break
        
        # Second attacker
        damage = second.calculate_damage(first)
        first.take_damage(damage)
        battle_log.append(f"💥 {second.name} attacks {first.name} for {damage} damage!")
        battle_log.append(f"   {first.name} HP: {first.hp}/{first.max_hp}")
        
        battle_log.append("")
        turn += 1
        
        # Safety check: max 50 turns
        if turn > 50:
            battle_log.append("⏱️ Battle timeout - Draw!")
            break
    
    # Battle result
    battle_log.append("=" * 40)
    if knight.is_alive:
        battle_log.append(f"🎉 Victory! {knight.name} defeated the {monster_combatant.name}!")
        battle_log.append(f"💚 {knight.name} HP remaining: {knight.hp}/{knight.max_hp}")
        battle_log.append(f"⭐ Experience gained: {monster.xp_reward} XP")
        result = 'victory'
        knight_alive = True
    elif monster_combatant.is_alive:
        battle_log.append(f"💀 Defeat! {knight.name} was slain by the {monster_combatant.name}!")
        battle_log.append(f"⚰️  {knight.name} has died permanently...")
        result = 'defeat'
        knight_alive = False
    else:
        battle_log.append("🤝 Draw! Both combatants fell!")
        battle_log.append(f"⚰️  {knight.name} has died permanently...")
        result = 'draw'
        knight_alive = False
    
    # Ensure HP is 0 if knight died
    if not knight_alive:
        knight.hp = 0
    
    return {
        'result': result,
        'knight_hp': knight.hp,
        'knight_alive': knight_alive,
        'log': battle_log,
        'xp_gained': monster.xp_reward if result == 'victory' else 0
    }
