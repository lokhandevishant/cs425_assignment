import os
import psycopg
from psycopg.rows import dict_row
import jwt
import datetime
from flask import Flask, request, jsonify, render_template
from functools import wraps
from dotenv import load_dotenv
load_dotenv()



app = Flask(__name__)
DB_URL = os.environ.get("DATABASE_URL")
SECRET_KEY = "super_secret_jwt_key_for_testing"

def get_db_connection():
    conn = psycopg.connect(DB_URL, row_factory=dict_row)
    return conn

# --- Middleware for verifying JWT token ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(" ")[1] # Remove 'Bearer '
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_role = data['role_id']
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user_role, *args, **kwargs)
    return decorated

# --- Frontend Routes ---
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# --- API Routes ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    login_id = data.get('loginId')
    pwd = data.get('pwd')

    conn = get_db_connection()
    # Updated cursor for Psycopg 3
    cursor = conn.cursor(row_factory=dict_row) 
    
    cursor.execute('SELECT * FROM Users WHERE LoginId = %s AND Pwd = %s', (login_id, pwd))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if user:
        token = jwt.encode({
            'user_id': user['userid'],
            'role_id': user['roleid'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({'token': token, 'userName': user['username']})
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/activities', methods=['GET'])
@token_required
def get_activities(current_user_role):
    conn = get_db_connection()
    # Updated cursor for Psycopg 3
    cursor = conn.cursor(row_factory=dict_row) 
    
    query = """
        SELECT a.ActivityId, a.ActivityName, a.AccessDetail 
        FROM Activity a
        JOIN Responsibility r ON a.ActivityId = r.ActivityId
        WHERE r.RoleId = %s
    """
    cursor.execute(query, (current_user_role,))
    activities = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return jsonify([dict(row) for row in activities])

if __name__ == '__main__':
    app.run(debug=True, port=5000)