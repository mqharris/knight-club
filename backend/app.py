from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import os

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
            "SELECT id, name, class, level, created_at FROM knights WHERE user_id = %s ORDER BY created_at DESC",
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
            "SELECT id, user_id, name, class, level, created_at FROM knights WHERE id = %s",
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
        
        # Check if all existing knights are level 10
        cursor.execute(
            "SELECT level FROM knights WHERE user_id = %s",
            (user_id,)
        )
        existing_knights = cursor.fetchall()
        
        if existing_knights and not all(k['level'] >= 10 for k in existing_knights):
            cursor.close()
            conn.close()
            return jsonify({'error': 'All knights must be level 10 before creating a new one'}), 400
        
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
