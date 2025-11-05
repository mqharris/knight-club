from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import os
from monsters import get_monster
from battle import simulate_battle

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
        cursor.close()
        conn.close()
        
        if not knight:
            return jsonify({'error': 'Knight not found'}), 404
        
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
        
        # Get monster
        monster = get_monster(difficulty)
        
        # Simulate battle
        battle_result = simulate_battle(knight, monster)
        
        # Update knight HP, alive status, and XP if victorious
        if battle_result['result'] == 'victory':
            new_exp = knight['exp'] + battle_result['xp_gained']
            
            cursor.execute(
                "UPDATE knights SET current_hp = %s, is_alive = %s, exp = %s WHERE id = %s",
                (battle_result['knight_hp'], battle_result['knight_alive'], new_exp, knight_id)
            )
        else:
            cursor.execute(
                "UPDATE knights SET current_hp = %s, is_alive = %s WHERE id = %s",
                (battle_result['knight_hp'], battle_result['knight_alive'], knight_id)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'result': battle_result['result'],
            'knight_hp': battle_result['knight_hp'],
            'knight_max_hp': knight['max_hp'],
            'knight_alive': battle_result['knight_alive'],
            'log': battle_result['log'],
            'xp_gained': battle_result['xp_gained']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/regen', methods=['POST'])
def regen_hp():
    """
    Regenerate HP for all knights (1 HP per 15 minutes).
    Called by K8s CronJob.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Heal all knights by 1 HP, up to their max_hp
        cursor.execute("""
            UPDATE knights 
            SET current_hp = LEAST(current_hp + 1, max_hp)
            WHERE current_hp < max_hp
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
