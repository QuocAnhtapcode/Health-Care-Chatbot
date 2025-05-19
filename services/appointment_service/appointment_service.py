from services.database_service.db_service import DatabaseService
from typing import Dict, Any, List, Tuple
from datetime import datetime, time

class AppointmentService:
    def __init__(self):
        self.db_service = DatabaseService()

    def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Chuyển đổi chuỗi ngày và giờ thành datetime và time objects
            appointment_date = datetime.strptime(appointment_data['date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(appointment_data['time'], '%H:%M').time()
            
            success = self.db_service.create_appointment(
                name=appointment_data.get('name'),
                phone=appointment_data.get('phone'),
                address=appointment_data.get('address'),
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                description=appointment_data.get('description')
            )
            return {
                'success': success,
                'message': 'Appointment created successfully' if success else 'Failed to create appointment'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating appointment: {str(e)}'
            }

    def get_all_appointments(self) -> Dict[str, Any]:
        try:
            appointments = self.db_service.get_all_appointments()
            # Chuyển đổi datetime và time objects thành chuỗi
            formatted_appointments = []
            for appt in appointments:
                formatted_appt = list(appt)
                if isinstance(appt[4], datetime):
                    formatted_appt[4] = appt[4].strftime('%Y-%m-%d')
                if isinstance(appt[5], time):
                    formatted_appt[5] = appt[5].strftime('%H:%M')
                formatted_appointments.append(formatted_appt)
            
            return {
                'success': True,
                'appointments': formatted_appointments
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching appointments: {str(e)}'
            }

    def get_available_slots(self, date_str: str) -> List[str]:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            available_slots = self.db_service.get_available_slots(date)
            # Chuyển đổi time objects thành chuỗi HH:MM
            return [slot.strftime('%H:%M') for slot in available_slots]
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return []

    def close(self):
        self.db_service.close() 