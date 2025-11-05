from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import os
import random
from monsters import get_monster
from battle import simulate_battle
from items import get_item

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'mysql'),
        port=int(os.getenv('DB_PORT', '3306')),
        database=os.getenv('DB_NAME', 'knightclub'),
        user=os.getenv('DB_USER', 'app'),
        password=os.getenv('DB_PASSWORD', 'password')
    )

def add_item_to_inventory(cursor, user_id, item_id, quantity=1):
    """Add item to user's inventory. Stacks if stackable, creates new row if not."""
    item_def = get_item(item_id)
    if not item_def:
        return False
    
    if item_def['stackable']:
        # Try to add to existing stack (not equipped)
        cursor.execute("""
            SELECT id, quantity FROM inventory 
            WHERE user_id = %s AND item_id = %s AND equipped_to_knight_id IS NULL
            LIMIT 1
        """, (user_id, item_id))
        
        existing = cursor.fetchone()
        if existing:
            # Update existing stack
            cursor.execute("""
                UPDATE inventory SET quantity = quantity + %s 
                WHERE id = %s
            """, (quantity, existing[0]))
        else:
            # Create new stack
            cursor.execute("""
                INSERT INTO inventory (user_id, item_id, quantity) 
                VALUES (%s, %s, %s)
            """, (user_id, item_id, quantity))
    else:
        # Non-stackable: create separate rows
        for _ in range(quantity):
            cursor.execute("""
                INSERT INTO inventory (user_id, item_id, quantity) 
                VALUES (%s, %s, 1)
            """, (user_id, item_id))
    
    return True

def generate_loot(monster):
    """Generate loot drops from monster."""
    loot = {
        'gold': random.randint(monster.gold_drop[0], monster.gold_drop[1]),
        'items': []
    }
    
    # Roll for each item in loot table
    for item_id, drop_chance in monster.loot_table:
        if random.random() < drop_chance:
            loot['items'].append(item_id)
    
    return loot

@app.route('/healthz')
def healthz():
    return 'OK', 200

@app.route('/livez')
def livez():
    return 'OK', 200

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'message': 'User created', 'user_id': user_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE username = %s",
            (username,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and bcrypt.checkpw(password.encode('utf-8'), bytes(result[1])):
            return jsonify({'message': 'Login successful', 'user_id': result[0]}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knights', methods=['GET'])
def get_knights():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, class, level, exp, current_hp, max_hp, is_alive, created_at FROM knights WHERE user_id = %s ORDER BY is_alive DESC, created_at DESC",
            (user_id,)
        )
        knights = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'knights': knights}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knights/<int:knight_id>', methods=['GET'])
def get_knight(knight_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, user_id, name, class, level, exp, current_hp, max_hp, is_alive, created_at FROM knights WHERE id = %s",
            (knight_id,)
        )
        knight = cursor.fetchone()
        
        if not knight:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Knight not found'}), 404
        
        # Get equipped items
        cursor.execute("""
            SELECT i.id, i.item_id, i.quantity
            FROM inventory i
            WHERE i.equipped_to_knight_id = %s
        """, (knight_id,))
        
        equipped_items = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Enrich equipped items with definitions
        equipment = []
        for item in equipped_items:
            item_def = get_item(item['item_id'])
            if item_def:
                equipment.append({
                    'inventory_id': item['id'],
                    'item_id': item['item_id'],
                    'name': item_def['name'],
                    'slot': item_def.get('slot'),
                    'stats': item_def.get('stats', {}),
                    'type': item_def['type']
                })
        
        knight['equipment'] = equipment
        
        return jsonify({'knight': knight}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knights', methods=['POST'])
def create_knight():
    data = request.json
    user_id = data.get('user_id')
    name = data.get('name')
    knight_class = data.get('class')
    
    if not user_id or not name or not knight_class:
        return jsonify({'error': 'user_id, name, and class required'}), 400
    
    if knight_class not in ['knight', 'paladin', 'lancer', 'templar']:
        return jsonify({'error': 'Invalid class'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if all existing LIVING knights are level 10
        cursor.execute(
            "SELECT level FROM knights WHERE user_id = %s AND is_alive = TRUE",
            (user_id,)
        )
        living_knights = cursor.fetchall()
        
        if living_knights and not all(k['level'] >= 10 for k in living_knights):
            cursor.close()
            conn.close()
            return jsonify({'error': 'All living knights must be level 10 before creating a new one'}), 400
        
        # Create the knight
        cursor.execute(
            "INSERT INTO knights (user_id, name, class, level) VALUES (%s, %s, %s, 1)",
            (user_id, name, knight_class)
        )
        conn.commit()
        knight_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'message': 'Knight created', 'knight_id': knight_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Knight name already exists for this user'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knights/<int:knight_id>/equip', methods=['POST'])
def equip_item(knight_id):
    """Equip an item to a knight."""
    data = request.json
    inventory_id = data.get('inventory_id')
    
    if not inventory_id:
        return jsonify({'error': 'inventory_id required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get knight info
        cursor.execute(
            "SELECT id, user_id FROM knights WHERE id = %s",
            (knight_id,)
        )
        knight = cursor.fetchone()
        
        if not knight:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Knight not found'}), 404
        
        # Get item from inventory
        cursor.execute("""
            SELECT i.id, i.item_id, i.user_id, i.equipped_to_knight_id
            FROM inventory i
            WHERE i.id = %s AND i.user_id = %s
        """, (inventory_id, knight['user_id']))
        
        inventory_item = cursor.fetchone()
        
        if not inventory_item:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Item not found in inventory'}), 404
        
        if inventory_item['equipped_to_knight_id'] is not None:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Item is already equipped'}), 400
        
        # Get item definition
        item_def = get_item(inventory_item['item_id'])
        if not item_def:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Invalid item'}), 400
        
        if item_def['stackable']:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cannot equip stackable items'}), 400
        
        # Check if slot already has an item equipped
        slot = item_def.get('slot')
        if slot:
            # Get all equipped items for this knight to check their slots
            cursor.execute("""
                SELECT i.id, i.item_id
                FROM inventory i
                WHERE i.equipped_to_knight_id = %s
            """, (knight_id,))
            
            equipped_items = cursor.fetchall()
            
            # Check if any equipped item uses the same slot
            for equipped in equipped_items:
                equipped_def = get_item(equipped['item_id'])
                if equipped_def and equipped_def.get('slot') == slot:
                    # Unequip the existing item in this slot
                    cursor.execute("""
                        UPDATE inventory
                        SET equipped_to_knight_id = NULL
                        WHERE id = %s
                    """, (equipped['id'],))
        
        # Equip the new item
        cursor.execute("""
            UPDATE inventory
            SET equipped_to_knight_id = %s
            WHERE id = %s
        """, (knight_id, inventory_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Item equipped successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knights/<int:knight_id>/unequip', methods=['POST'])
def unequip_item(knight_id):
    """Unequip an item from a knight."""
    data = request.json
    inventory_id = data.get('inventory_id')
    
    if not inventory_id:
        return jsonify({'error': 'inventory_id required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify item is equipped to this knight
        cursor.execute("""
            SELECT id FROM inventory
            WHERE id = %s AND equipped_to_knight_id = %s
        """, (inventory_id, knight_id))
        
        item = cursor.fetchone()
        
        if not item:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Item not equipped to this knight'}), 404
        
        # Unequip the item
        cursor.execute("""
            UPDATE inventory
            SET equipped_to_knight_id = NULL
            WHERE id = %s
        """, (inventory_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Item unequipped successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Get user's inventory."""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user's gold
        cursor.execute("SELECT gold FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Get inventory items
        cursor.execute("""
            SELECT id, item_id, quantity, equipped_to_knight_id, created_at
            FROM inventory
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Enrich with item definitions
        enriched_items = []
        for item in items:
            item_def = get_item(item['item_id'])
            if item_def:
                enriched_items.append({
                    **item,
                    'name': item_def['name'],
                    'type': item_def['type'],
                    'stackable': item_def['stackable'],
                    'stats': item_def.get('stats', {}),
                    'slot': item_def.get('slot'),
                    'rarity': item_def.get('rarity', 'common')
                })
        
        return jsonify({
            'gold': user['gold'] if user else 0,
            'items': enriched_items
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/battle', methods=['POST'])
def start_battle():
    data = request.json
    knight_id = data.get('knight_id')
    difficulty = data.get('difficulty', 'easy')
    
    if not knight_id:
        return jsonify({'error': 'knight_id required'}), 400
    
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get knight data
        cursor.execute(
            "SELECT id, user_id, name, class, level, exp, current_hp, max_hp FROM knights WHERE id = %s",
            (knight_id,)
        )
        knight = cursor.fetchone()
        
        if not knight:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Knight not found'}), 404
        
        # Check if knight has enough HP to battle
        if knight['current_hp'] <= 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Knight has no HP remaining'}), 400
        
        # Get equipped items and calculate stat bonuses
        cursor.execute("""
            SELECT i.item_id
            FROM inventory i
            WHERE i.equipped_to_knight_id = %s
        """, (knight_id,))
        
        equipped_items = cursor.fetchall()
        
        # Calculate total stat bonuses from equipment
        attack_bonus = 0
        defense_bonus = 0
        agility_bonus = 0
        
        for item in equipped_items:
            item_def = get_item(item['item_id'])
            if item_def and 'stats' in item_def:
                attack_bonus += item_def['stats'].get('attack', 0)
                defense_bonus += item_def['stats'].get('defense', 0)
                agility_bonus += item_def['stats'].get('agility', 0)
        
        # Add bonuses to knight data
        knight['attack_bonus'] = attack_bonus
        knight['defense_bonus'] = defense_bonus
        knight['agility_bonus'] = agility_bonus
        
        # Get monster
        monster = get_monster(difficulty)
        
        # Simulate battle
        battle_result = simulate_battle(knight, monster)
        
        # Initialize exp and level for response
        new_exp = knight['exp']
        new_level = knight['level']
        
        # Update knight HP, alive status, and XP if victorious
        if battle_result['result'] == 'victory':
            new_exp = knight['exp'] + battle_result['xp_gained']
            new_level = (new_exp // 100) + 1  # Level up every 100 XP
            
            # Generate loot
            loot = generate_loot(monster)
            
            # Award gold
            cursor.execute(
                "UPDATE users SET gold = gold + %s WHERE id = %s",
                (loot['gold'], knight['user_id'])
            )
            
            # Award items
            for item_id in loot['items']:
                add_item_to_inventory(cursor, knight['user_id'], item_id, 1)
            
            # Update knight stats
            cursor.execute(
                "UPDATE knights SET current_hp = %s, is_alive = %s, exp = %s, level = %s WHERE id = %s",
                (battle_result['knight_hp'], battle_result['knight_alive'], new_exp, new_level, knight_id)
            )
            
            battle_result['exp'] = new_exp
            battle_result['level'] = new_level
            
            # Build loot items list, skipping any invalid items
            loot_items = []
            for item_id in loot['items']:
                item_def = get_item(item_id)
                if item_def:
                    loot_items.append({'id': item_id, 'name': item_def['name']})
            
            battle_result['loot'] = {
                'gold': loot['gold'],
                'items': loot_items
            }
        else:
            cursor.execute(
                "UPDATE knights SET current_hp = %s, is_alive = %s WHERE id = %s",
                (battle_result['knight_hp'], battle_result['knight_alive'], knight_id)
            )
            
            battle_result['exp'] = knight['exp']
            battle_result['level'] = knight['level']
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'result': battle_result['result'],
            'knight_hp': battle_result['knight_hp'],
            'knight_max_hp': knight['max_hp'],
            'knight_alive': battle_result['knight_alive'],
            'log': battle_result['log'],
            'xp_gained': battle_result['xp_gained'],
            'exp': new_exp,
            'level': new_level,
            'loot': battle_result.get('loot', {'gold': 0, 'items': []})
        }), 200
        
    except TypeError as e:
        import traceback
        error_msg = f"TypeError in battle: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({'error': error_msg}), 500
    except KeyError as e:
        import traceback
        error_msg = f"KeyError in battle: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        import traceback
        error_msg = str(e) if str(e) else 'Unknown error occurred'
        print(f"Battle error: {error_msg}")
        print(traceback.format_exc())
        return jsonify({'error': error_msg}), 500

@app.route('/api/regen', methods=['POST'])
def regen_hp():
    """
    Regenerate HP for all knights (1 HP per 15 minutes).
    Called by K8s CronJob.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Heal all LIVING knights by 1 HP, up to their max_hp
        cursor.execute("""
            UPDATE knights 
            SET current_hp = LEAST(current_hp + 1, max_hp)
            WHERE current_hp < max_hp AND is_alive = TRUE
        """)
        
        healed_count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': f'Healed {healed_count} knights',
            'healed_count': healed_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
