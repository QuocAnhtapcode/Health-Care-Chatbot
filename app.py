from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from dotenv import load_dotenv
import os
from datetime import datetime, time, timedelta
from typing import List
from functools import wraps

from services.chat_service.chat_service import ChatService
from services.appointment_service.appointment_service import AppointmentService
from services.vector_store_service.vector_service import VectorStoreService
from services.user_service.user_service import UserService
from services.prescription_service.prescription_service import PrescriptionService

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize services
chat_service = ChatService()
appointment_service = AppointmentService()
vector_service = VectorStoreService()
user_service = UserService()
prescription_service = PrescriptionService()

# Thiết lập secret key
app.secret_key = os.urandom(24)  # Tạo một secret key ngẫu nhiên

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        # Kiểm tra xem user có phải là admin không (giả sử admin có id = 1)
        if session.get('user_id') != 1:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        result = user_service.login_user(username, password)
        if result['success']:
            session['user_id'] = result['user']['id']
            session['username'] = result['user']['username']
            return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = {
            'username': request.form['username'],
            'email': request.form['email'],
            'password': request.form['password'],
            'full_name': request.form['full_name'],
            'phone': request.form['phone']
        }
        
        result = user_service.register_user(user_data)
        if result['success']:
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/chat")
@login_required
def chat_page():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
@login_required
def chat():
    msg = request.form["msg"]
    response = chat_service.get_response(msg)
    return str(response["answer"])

@app.route("/get-available-slots", methods=["POST"])
@login_required
def get_available_slots():
    """API lấy danh sách các khung giờ còn trống cho một ngày cụ thể."""
    date = request.form.get("date")
    if not date:
        return jsonify({"error": "Date is required"}), 400
    slots = appointment_service.get_available_slots(date)
    return jsonify({"slots": slots})

@app.route('/book', methods=['POST'])
@login_required
def book_appointment():
    try:
        appointment_data = {
            'user_id': session['user_id'],
            'name': request.form['name'],
            'phone': request.form['phone'],
            'address': request.form['address'],
            'date': request.form['date'],
            'time': request.form['time'],
            'description': request.form['description']
        }
        print("[app.py] Dữ liệu nhận được từ form:", appointment_data)

        result = appointment_service.create_appointment(appointment_data)
        print("[app.py] Kết quả trả về:", result)

        if result['success']:
            return redirect(url_for('index'))
    except Exception as e:
        return redirect(url_for('index'))

@app.route("/admin/appointments")
@admin_required
def admin_appointments():
    result = appointment_service.get_all_appointments()
    return render_template("admin_appointments.html", appointments=result['appointments'])

@app.route("/prescriptions")
@login_required
def view_prescriptions():
    result = prescription_service.get_user_prescriptions(session['user_id'])
    return render_template("prescriptions.html", prescriptions=result['prescriptions'])

@app.route("/admin/prescriptions", methods=['GET', 'POST'])
@admin_required
def admin_prescriptions():
    result = prescription_service.get_all_prescriptions()
    users = user_service.get_all_users()
    return render_template("admin_prescriptions.html", 
                         prescriptions=result['prescriptions'],
                         users=users)

@app.route("/admin/prescriptions/create", methods=['POST'])
@admin_required
def create_prescription():
    try:
        prescription_data = {
            'user_id': request.form['user_id'],
            'doctor_name': request.form['doctor_name'],
            'diagnosis': request.form['diagnosis'],
            'medications': request.form['medications'],
            'notes': request.form.get('notes', '')
        }
        
        result = prescription_service.create_prescription(prescription_data)
        if result['success']:
            return redirect(url_for('admin_prescriptions'))
    except Exception as e:
        return redirect(url_for('admin_prescriptions'))

if __name__ == '__main__':
    try:
        app.run(host="0.0.0.0", port=8080, debug=True)
    finally:
        appointment_service.close()
        user_service.close()
        prescription_service.close()
