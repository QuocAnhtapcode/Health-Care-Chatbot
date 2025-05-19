import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

class UserService:
    def __init__(self):
        load_dotenv()
        self.connection = None
        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', '1234'),
                database=os.getenv('DB_NAME', 'healthcare')
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                self.create_users_table()
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def create_users_table(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"Error creating users table: {e}")

    def register_user(self, user_data):
        try:
            cursor = self.connection.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s",
                         (user_data['username'], user_data['email']))
            if cursor.fetchone():
                return {'success': False, 'message': 'Username or email already exists'}

            # Hash the password
            password_hash = generate_password_hash(user_data['password'])

            # Insert new user
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, phone)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user_data['username'],
                user_data['email'],
                password_hash,
                user_data.get('full_name', ''),
                user_data.get('phone', '')
            ))
            
            self.connection.commit()
            cursor.close()
            return {'success': True, 'message': 'User registered successfully'}
        except Error as e:
            print(f"Error registering user: {e}")
            return {'success': False, 'message': str(e)}

    def login_user(self, username, password):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()

            if user and check_password_hash(user['password_hash'], password):
                return {
                    'success': True,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'full_name': user['full_name']
                    }
                }
            return {'success': False, 'message': 'Invalid username or password'}
        except Error as e:
            print(f"Error logging in: {e}")
            return {'success': False, 'message': str(e)}

    def get_user_by_id(self, user_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT id, username, email, full_name, phone FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"Error getting user: {e}")
            return None

    def get_all_users(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT id, username, full_name FROM users")
            users = cursor.fetchall()
            cursor.close()
            return users
        except Exception as e:
            print(f"Error fetching all users: {e}")
            return []

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed") 