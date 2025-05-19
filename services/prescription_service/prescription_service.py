from services.database_service.db_service import DatabaseService
from typing import Dict, Any, List, Tuple
from datetime import datetime

class PrescriptionService:
    def __init__(self):
        self.db_service = DatabaseService()

    def create_prescription(self, prescription_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            success = self.db_service.create_prescription(
                user_id=prescription_data['user_id'],
                doctor_name=prescription_data.get('doctor_name'),
                diagnosis=prescription_data.get('diagnosis'),
                medications=prescription_data.get('medications'),
                notes=prescription_data.get('notes'),
                prescription_date=datetime.now().date()
            )
            
            return {
                'success': success,
                'message': 'Prescription created successfully' if success else 'Failed to create prescription'
            }
        except Exception as e:
            print("[prescription_service.py] Error:", e)
            return {
                'success': False,
                'message': f'Error creating prescription: {str(e)}'
            }

    def get_user_prescriptions(self, user_id: int) -> Dict[str, Any]:
        try:
            prescriptions = self.db_service.get_user_prescriptions(user_id)
            formatted_prescriptions = []
            for pres in prescriptions:
                formatted_pres = list(pres)
                if isinstance(pres[5], datetime):
                    formatted_pres[5] = pres[5].strftime('%Y-%m-%d')
                formatted_prescriptions.append(formatted_pres)
            
            return {
                'success': True,
                'prescriptions': formatted_prescriptions
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching prescriptions: {str(e)}'
            }

    def get_all_prescriptions(self) -> Dict[str, Any]:
        try:
            prescriptions = self.db_service.get_all_prescriptions()
            formatted_prescriptions = []
            for pres in prescriptions:
                formatted_pres = list(pres)
                if isinstance(pres[5], datetime):
                    formatted_pres[5] = pres[5].strftime('%Y-%m-%d')
                formatted_prescriptions.append(formatted_pres)
            
            return {
                'success': True,
                'prescriptions': formatted_prescriptions
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching prescriptions: {str(e)}'
            }

    def close(self):
        self.db_service.close() 