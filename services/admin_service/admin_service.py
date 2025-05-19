import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

class AdminService:
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
                print("Connected to MySQL database (admin)")
                self.create_admins_table()
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def create_admins_table(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print(f"Error creating admins table: {e}")

    def register_admin(self, admin_data):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM admins WHERE username = %s OR email = %s",
                         (admin_data['username'], admin_data['email']))
            if cursor.fetchone():
                return {'success': False, 'message': 'Username or email already exists'}
            password_hash = generate_password_hash(admin_data['password'])
            cursor.execute("""
                INSERT INTO admins (username, email, password_hash, full_name)
                VALUES (%s, %s, %s, %s)
            """, (
                admin_data['username'],
                admin_data['email'],
                password_hash,
                admin_data.get('full_name', '')
            ))
            self.connection.commit()
            cursor.close()
            return {'success': True, 'message': 'Admin registered successfully'}
        except Error as e:
            print(f"Error registering admin: {e}")
            return {'success': False, 'message': str(e)}

    def login_admin(self, username, password):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            admin = cursor.fetchone()
            cursor.close()
            if admin and check_password_hash(admin['password_hash'], password):
                return {
                    'success': True,
                    'admin': {
                        'id': admin['id'],
                        'username': admin['username'],
                        'email': admin['email'],
                        'full_name': admin['full_name']
                    }
                }
            return {'success': False, 'message': 'Invalid username or password'}
        except Error as e:
            print(f"Error logging in admin: {e}")
            return {'success': False, 'message': str(e)}

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed (admin)") 