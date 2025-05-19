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