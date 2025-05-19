import mysql.connector
from typing import List, Tuple, Dict, Any
from datetime import datetime, time

class DatabaseService:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="healthcare"
        )
        self.cursor = self.connection.cursor()

    def create_appointment(self, name: str, phone: str, address: str, 
                         appointment_date: datetime, appointment_time: time,
                         description: str) -> bool:
        try:
            sql = """
                INSERT INTO appointments 
                (name, phone, address, appointment_date, appointment_time, description) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(sql, (name, phone, address, appointment_date, 
                                    appointment_time, description))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error creating appointment: {e}")
            return False

    def get_all_appointments(self) -> List[Tuple]:
        try:
            self.cursor.execute("""
                SELECT * FROM appointments 
                ORDER BY appointment_date, appointment_time
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching appointments: {e}")
            return []

    def get_available_slots(self, date: datetime) -> List[time]:
        try:
            # Lấy tất cả các slot đã đặt cho ngày cụ thể
            sql = """
                SELECT appointment_time 
                FROM appointments 
                WHERE appointment_date = %s
            """
            self.cursor.execute(sql, (date,))
            booked_slots = [row[0] for row in self.cursor.fetchall()]

            # Tạo danh sách tất cả các slot có thể đặt (30 phút một slot)
            all_slots = []
            start_time = time(8, 0)  # 8:00 AM
            end_time = time(22, 0)   # 10:00 PM

            current_time = start_time
            while current_time < end_time:
                if current_time not in booked_slots:
                    all_slots.append(current_time)
                # Thêm 30 phút
                current_time = time(
                    current_time.hour + (current_time.minute + 30) // 60,
                    (current_time.minute + 30) % 60
                )

            return all_slots
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return []

    def close(self):
        self.cursor.close()
        self.connection.close() 