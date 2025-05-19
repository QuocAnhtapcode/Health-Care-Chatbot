import mysql.connector
from typing import List, Tuple, Dict, Any
from datetime import datetime, time, timedelta


class DatabaseService:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="healthcare"
        )
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        try:
            # Create appointments table with user_id
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    address TEXT NOT NULL,
                    appointment_date DATE NOT NULL,
                    appointment_time TIME NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Create prescriptions table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    doctor_name VARCHAR(100) NOT NULL,
                    diagnosis TEXT NOT NULL,
                    medications TEXT NOT NULL,
                    notes TEXT,
                    prescription_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            self.connection.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")

    def create_appointment(self, user_id: int, name: str, phone: str, address: str, 
                         appointment_date: datetime, appointment_time: time,
                         description: str) -> bool:
        try:
            sql = """
                INSERT INTO appointments 
                (user_id, name, phone, address, appointment_date, appointment_time, description) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (user_id, name, phone, address, appointment_date, 
                                    appointment_time, description))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error creating appointment: {e}")
            return False

    def create_prescription(self, user_id: int, doctor_name: str, diagnosis: str,
                          medications: str, notes: str, prescription_date: datetime) -> bool:
        try:
            sql = """
                INSERT INTO prescriptions 
                (user_id, doctor_name, diagnosis, medications, notes, prescription_date) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (user_id, doctor_name, diagnosis, medications, 
                                    notes, prescription_date))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error creating prescription: {e}")
            return False

    def get_user_prescriptions(self, user_id: int) -> List[Tuple]:
        try:
            self.cursor.execute("""
                SELECT p.*, u.username 
                FROM prescriptions p
                JOIN users u ON p.user_id = u.id
                WHERE p.user_id = %s
                ORDER BY p.prescription_date DESC
            """, (user_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching user prescriptions: {e}")
            return []

    def get_all_prescriptions(self) -> List[Tuple]:
        try:
            self.cursor.execute("""
                SELECT p.*, u.username 
                FROM prescriptions p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.prescription_date DESC
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching all prescriptions: {e}")
            return []

    def get_all_appointments(self) -> List[Tuple]:
        try:
            self.cursor.execute("""
                SELECT a.*, u.username 
                FROM appointments a
                JOIN users u ON a.user_id = u.id
                ORDER BY appointment_date, appointment_time
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching appointments: {e}")
            return []

    def get_available_slots(self, date: datetime) -> List[time]:
        try:
            sql = """
                SELECT appointment_time 
                FROM appointments 
                WHERE appointment_date = %s
            """
            self.cursor.execute(sql, (date,))
            booked_slots_raw = self.cursor.fetchall()

            # Ép kiểu về time nếu là timedelta
            booked_slots = [
                (datetime.min + row[0]).time() if isinstance(row[0], timedelta) else row[0]
                for row in booked_slots_raw
            ]
            print("[db_service.py] Các slot đã được đặt:", booked_slots)

            all_slots = []
            start_time = time(8, 0)
            end_time = time(22, 0)
            current_time = start_time

            while current_time < end_time:
                if current_time not in booked_slots:
                    all_slots.append(current_time)
                current_time = time(
                    current_time.hour + (current_time.minute + 30) // 60,
                    (current_time.minute + 30) % 60
                )

            print("[db_service.py] Slot khả dụng trả về:", all_slots)
            return all_slots
        except Exception as e:
            print("[db_service.py] Lỗi:", e)
            return []
    
    def close(self):
        self.cursor.close()
        self.connection.close() 