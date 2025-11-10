from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import os
import random
import sys
import logging
from monsters import get_monster
from battle import simulate_battle
from items import get_item

app = Flask(__name__)
CORS(app)

# Configure logging to stderr
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'mysql'),
        port=int(os.getenv('DB_PORT', '3306')),
        database=os.getenv('DB_NAME', 'knightclub'),
        user=os.getenv('DB_USER', 'app'),
        password=os.getenv('DB_PASSWORD', 'password')
    )

def verify_knight_ownership(cursor, knight_id, user_id):
    """Verify that a knight belongs to a specific user."""
    cursor.execute("SELECT user_id FROM knights WHERE id = %s", (knight_id,))
    knight = cursor.fetchone()
    if not knight:
        return False
    return knight['user_id'] == user_id

def add_item_to_inventory(cursor, knight_id, item_id, quantity=1):
    """Add item to knight's inventory. Stacks if stackable, creates new row if not."""
    item_def = get_item(item_id)
    if not item_def:
        return False
    
    if item_def['stackable']:
        # Try to add to existing stack (not equipped)
        cursor.execute("""
            SELECT id, quantity FROM inventory 
            WHERE knight_id = %s AND item_id = %s AND is_equipped = FALSE
            LIMIT 1
        """, (knight_id, item_id))
        
        existing = cursor.fetchone()
        if existing:
            # Update existing stack
            cursor.execute("""
                UPDATE inventory SET quantity = quantity + %s 
                WHERE id = %s
            """, (quantity, existing['id']))
        else:
            # Create new stack
            cursor.execute("""
                INSERT INTO inventory (knight_id, item_id, quantity) 
                VALUES (%s, %s, %s)
            """, (knight_id, item_id, quantity))
    else:
        # Non-stackable: create separate rows
        for _ in range(quantity):
            cursor.execute("""
                INSERT INTO inventory (knight_id, item_id, quantity) 
                VALUES (%s, %s, 1)
            """, (knight_id, item_id))
    
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

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    """Get top 10 living knights by level and exp"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT k.name, k.class, k.level, k.exp, u.username
            FROM knights k
            JOIN users u ON k.user_id = u.id
            WHERE k.is_alive = TRUE
            ORDER BY k.level DESC, k.exp DESC
            LIMIT 10
        """)
        
        knights = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(knights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
            WHERE i.knight_id = %s AND i.is_equipped = TRUE
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
    user_id = data.get('user_id')
    
    if not inventory_id or not user_id:
        return jsonify({'error': 'inventory_id and user_id required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify knight ownership
        if not verify_knight_ownership(cursor, knight_id, user_id):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Unauthorized: Knight does not belong to this user'}), 403
        
        # Get item from knight's inventory
        cursor.execute("""
            SELECT i.id, i.item_id, i.is_equipped
            FROM inventory i
            WHERE i.id = %s AND i.knight_id = %s
        """, (inventory_id, knight_id))
        
        inventory_item = cursor.fetchone()
        
        if not inventory_item:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Item not found in this knight\'s inventory'}), 404
        
        if inventory_item['is_equipped']:
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
                WHERE i.knight_id = %s AND i.is_equipped = TRUE
            """, (knight_id,))
            
            equipped_items = cursor.fetchall()
            
            # Check if any equipped item uses the same slot
            for equipped in equipped_items:
                equipped_def = get_item(equipped['item_id'])
                if equipped_def and equipped_def.get('slot') == slot:
                    # Unequip the existing item in this slot
                    cursor.execute("""
                        UPDATE inventory
                        SET is_equipped = FALSE
                        WHERE id = %s
                    """, (equipped['id'],))
        
        # Equip the new item
        cursor.execute("""
            UPDATE inventory
            SET is_equipped = TRUE
            WHERE id = %s
        """, (inventory_id,))
        
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
    user_id = data.get('user_id')
    
    if not inventory_id or not user_id:
        return jsonify({'error': 'inventory_id and user_id required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify knight ownership
        if not verify_knight_ownership(cursor, knight_id, user_id):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Unauthorized: Knight does not belong to this user'}), 403
        
        # Verify item is equipped to this knight
        cursor.execute("""
            SELECT id FROM inventory
            WHERE id = %s AND knight_id = %s AND is_equipped = TRUE
        """, (inventory_id, knight_id))
        
        item = cursor.fetchone()
        
        if not item:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Item not found or not equipped to this knight'}), 404
        
        # Unequip the item
        cursor.execute("""
            UPDATE inventory
            SET is_equipped = FALSE
            WHERE id = %s
        """, (inventory_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Item unequipped successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knights/<int:knight_id>/sell-duplicates', methods=['POST'])
def sell_duplicate_equipment(knight_id):
    """Sell all unequipped equipment items for gold."""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify knight ownership
        if not verify_knight_ownership(cursor, knight_id, user_id):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Unauthorized: Knight does not belong to this user'}), 403
        
        # Verify knight exists and get user_id
        cursor.execute("SELECT user_id FROM knights WHERE id = %s", (knight_id,))
        knight = cursor.fetchone()
        
        if not knight:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Knight not found'}), 404
        
        user_id = knight['user_id']
        
        # Get all unequipped equipment items
        cursor.execute("""
            SELECT id, item_id, quantity
            FROM inventory
            WHERE knight_id = %s AND is_equipped = FALSE
        """, (knight_id,))
        
        items = cursor.fetchall()
        
        total_gold = 0
        items_sold = 0
        
        for item in items:
            item_def = get_item(item['item_id'])
            
            # Only sell equipment (not materials)
            if item_def and not item_def.get('stackable', False):
                # Calculate sell price based on item tier
                item_id = item['item_id']
                if 200 <= item_id < 300:  # Wooden
                    sell_price = 10
                elif 300 <= item_id < 400:  # Stone
                    sell_price = 40
                elif 400 <= item_id < 500:  # Iron
                    sell_price = 100
                else:
                    sell_price = 5  # Default
                
                total_gold += sell_price
                items_sold += 1
                
                # Delete the item from inventory
                cursor.execute("DELETE FROM inventory WHERE id = %s", (item['id'],))
        
        # Add gold to user
        if total_gold > 0:
            cursor.execute("""
                UPDATE users
                SET gold = gold + %s
                WHERE id = %s
            """, (total_gold, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': f'Sold {items_sold} items for {total_gold} gold',
            'items_sold': items_sold,
            'gold_earned': total_gold
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knights/<int:knight_id>/use-potion', methods=['POST'])
def use_potion(knight_id):
    """Use an HP potion on a knight."""
    data = request.json
    user_id = data.get('user_id')
    inventory_id = data.get('inventory_id')
    
    if not user_id or not inventory_id:
        return jsonify({'error': 'user_id and inventory_id required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify knight ownership
        if not verify_knight_ownership(cursor, knight_id, user_id):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Unauthorized: Knight does not belong to this user'}), 403
        
        # Get the item from inventory
        cursor.execute("""
            SELECT id, item_id, quantity
            FROM inventory
            WHERE id = %s AND knight_id = %s
        """, (inventory_id, knight_id))
        
        inventory_item = cursor.fetchone()
        
        if not inventory_item:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Item not found in inventory'}), 404
        
        # Check if it's a potion
        item_def = get_item(inventory_item['item_id'])
        if not item_def or item_def['type'] != 'consumable':
            cursor.close()
            conn.close()
            return jsonify({'error': 'Item is not a consumable'}), 400
        
        # Get knight data
        cursor.execute("""
            SELECT current_hp, max_hp, is_alive
            FROM knights
            WHERE id = %s
        """, (knight_id,))
        
        knight = cursor.fetchone()
        
        if not knight:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Knight not found'}), 404
        
        if not knight['is_alive']:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cannot use potions on dead knights'}), 400
        
        if knight['current_hp'] >= knight['max_hp']:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Knight already at full HP'}), 400
        
        # Apply healing
        heal_amount = item_def['effect']['amount']
        new_hp = min(knight['current_hp'] + heal_amount, knight['max_hp'])
        actual_healing = new_hp - knight['current_hp']
        
        cursor.execute("""
            UPDATE knights
            SET current_hp = %s
            WHERE id = %s
        """, (new_hp, knight_id))
        
        # Remove one potion from inventory
        if inventory_item['quantity'] > 1:
            cursor.execute("""
                UPDATE inventory
                SET quantity = quantity - 1
                WHERE id = %s
            """, (inventory_id,))
        else:
            cursor.execute("DELETE FROM inventory WHERE id = %s", (inventory_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': f'Used {item_def["name"]}! Healed {actual_healing} HP',
            'new_hp': new_hp,
            'max_hp': knight['max_hp']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Get knight's inventory."""
    knight_id = request.args.get('knight_id')
    
    if not knight_id:
        return jsonify({'error': 'knight_id required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get knight's user_id for gold
        cursor.execute("SELECT user_id FROM knights WHERE id = %s", (knight_id,))
        knight = cursor.fetchone()
        if not knight:
            return jsonify({'error': 'Knight not found'}), 404
        
        # Get user's gold
        cursor.execute("SELECT gold FROM users WHERE id = %s", (knight['user_id'],))
        user = cursor.fetchone()
        
        # Get inventory items for this knight
        cursor.execute("""
            SELECT id, item_id, quantity, is_equipped, created_at
            FROM inventory
            WHERE knight_id = %s
            ORDER BY created_at DESC
        """, (knight_id,))
        
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
                    'rarity': item_def.get('rarity', 'common'),
                    'description': item_def.get('description', '')
                })
        
        return jsonify({
            'gold': user['gold'] if user else 0,
            'items': enriched_items
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/shop/items', methods=['GET'])
def get_shop_items():
    """Get all items available in the shop."""
    shop_items = [
        {
            'id': 501,
            'name': 'HP Potion',
            'description': 'Restores 25 HP when consumed',
            'price': 100,
            'type': 'consumable'
        }
    ]
    return jsonify(shop_items), 200

@app.route('/api/shop/buy', methods=['POST'])
def buy_shop_item():
    """Buy an item from the shop."""
    data = request.json
    user_id = data.get('user_id')
    knight_id = data.get('knight_id')
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    if not user_id or not knight_id or not item_id:
        return jsonify({'error': 'user_id, knight_id, and item_id required'}), 400
    
    if quantity < 1:
        return jsonify({'error': 'Quantity must be at least 1'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify knight ownership
        if not verify_knight_ownership(cursor, knight_id, user_id):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Unauthorized: Knight does not belong to this user'}), 403
        
        # Get item details
        item_def = get_item(item_id)
        if not item_def:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Item not found'}), 404
        
        # Check if item is available in shop (hardcoded for now)
        shop_prices = {
            501: 100  # HP Potion
        }
        
        if item_id not in shop_prices:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Item not available in shop'}), 400
        
        price = shop_prices[item_id]
        total_cost = price * quantity
        
        # Get user's gold
        cursor.execute("SELECT gold FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        if user['gold'] < total_cost:
            cursor.close()
            conn.close()
            return jsonify({'error': f'Not enough gold. Need {total_cost}, have {user["gold"]}'}), 400
        
        # Deduct gold
        cursor.execute("""
            UPDATE users
            SET gold = gold - %s
            WHERE id = %s
        """, (total_cost, user_id))
        
        # Add item to knight's inventory
        add_item_to_inventory(cursor, knight_id, item_id, quantity)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': f'Purchased {quantity}x {item_def["name"]} for {total_cost} gold',
            'gold_spent': total_cost
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/battle', methods=['POST'])
def start_battle():
    logger.error("=" * 80)
    logger.error("[BATTLE] BATTLE ENDPOINT CALLED - START")
    sys.stderr.flush()
    
    data = request.json
    knight_id = data.get('knight_id')
    user_id = data.get('user_id')
    difficulty = data.get('difficulty', 'easy')
    
    logger.error(f"[BATTLE] Received: knight_id={knight_id}, user_id={user_id}, difficulty={difficulty}")
    sys.stderr.flush()
    
    if not knight_id or not user_id:
        return jsonify({'error': 'knight_id and user_id required'}), 400
    
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400
    
    logger.error("[BATTLE] Validation passed, entering try block")
    sys.stderr.flush()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify knight ownership
        if not verify_knight_ownership(cursor, knight_id, user_id):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Unauthorized: Knight does not belong to this user'}), 403
        
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
            WHERE i.knight_id = %s AND i.is_equipped = TRUE
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
        logger.info(f"[BATTLE] Monster: {monster.name}, Difficulty: {difficulty}")
        
        # Simulate battle
        battle_result = simulate_battle(knight, monster)
        logger.info(f"[BATTLE] Battle result: {battle_result.get('result')}")
        logger.info(f"[BATTLE] Battle result keys: {list(battle_result.keys())}")
        
        # Initialize exp and level for response
        new_exp = knight['exp']
        new_level = knight['level']
        logger.info(f"[BATTLE] Initial exp: {new_exp}, level: {new_level}")
        
        # Update knight HP, alive status, and XP if victorious
        if battle_result['result'] == 'victory':
            logger.info("[BATTLE] Victory path")
            new_exp = knight['exp'] + battle_result['xp_gained']
            new_level = (new_exp // 100) + 1  # Level up every 100 XP
            logger.info(f"[BATTLE] New exp: {new_exp}, new level: {new_level}")
            
            # Generate loot
            loot = generate_loot(monster)
            logger.info(f"[BATTLE] Loot generated: gold={loot['gold']}, items={loot['items']}")
            
            # Award gold
            cursor.execute(
                "UPDATE users SET gold = gold + %s WHERE id = %s",
                (loot['gold'], knight['user_id'])
            )
            
            # Award items to this knight's inventory
            for item_id in loot['items']:
                logger.info(f"[BATTLE] Adding item {item_id} to inventory")
                add_item_to_inventory(cursor, knight_id, item_id, 1)
            
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
                logger.info(f"[BATTLE] Looking up item {item_id}")
                item_def = get_item(item_id)
                if item_def:
                    loot_items.append({'id': item_id, 'name': item_def['name']})
                    logger.info(f"[BATTLE] Added item: {item_def['name']}")
                else:
                    logger.warning(f"[BATTLE] WARNING: Item {item_id} not found!")
            
            battle_result['loot'] = {
                'gold': loot['gold'],
                'items': loot_items
            }
            logger.info(f"[BATTLE] Final loot: {battle_result['loot']}")
        else:
            logger.info("[BATTLE] Defeat path")
            cursor.execute(
                "UPDATE knights SET current_hp = %s, is_alive = %s WHERE id = %s",
                (battle_result['knight_hp'], battle_result['knight_alive'], knight_id)
            )
            
            battle_result['exp'] = knight['exp']
            battle_result['level'] = knight['level']
        
        logger.info(f"[BATTLE] About to commit. new_exp={new_exp}, new_level={new_level}")
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"[BATTLE] Returning response")
        return jsonify({
            'result': battle_result['result'],
            'knight_hp': battle_result['knight_hp'],
            'knight_max_hp': knight['max_hp'],
            'knight_alive': battle_result['knight_alive'],
            'log': battle_result['log'],
            'xp_gained': battle_result['xp_gained'],
            'exp': new_exp,
            'level': new_level,
            'loot': battle_result.get('loot', {'gold': 0, 'items': []}),
            'monster': {
                'name': monster.name,
                'hp': monster.max_hp,
                'attack': monster.attack,
                'defense': monster.defense,
                'agility': monster.agility
            }
        }), 200
        
    except TypeError as e:
        import traceback
        error_msg = f"TypeError in battle: {str(e)}"
        logger.error("!" * 80)
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        logger.error("!" * 80)
        sys.stderr.flush()
        return jsonify({'error': error_msg}), 500
    except KeyError as e:
        import traceback
        error_msg = f"KeyError in battle: {str(e)}"
        logger.error("!" * 80)
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        logger.error("!" * 80)
        sys.stderr.flush()
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        import traceback
        error_msg = str(e) if str(e) else 'Unknown error occurred'
        logger.error("!" * 80)
        logger.error(f"Battle error: {error_msg}")
        logger.error(f"Error type: {type(e)}")
        logger.error(traceback.format_exc())
        logger.error("!" * 80)
        sys.stderr.flush()
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
