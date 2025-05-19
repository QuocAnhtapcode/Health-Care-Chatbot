from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from dotenv import load_dotenv
import os
from datetime import datetime, time, timedelta
from typing import List

from services.chat_service.chat_service import ChatService
from services.appointment_service.appointment_service import AppointmentService
from services.vector_store_service.vector_service import VectorStoreService

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize services
chat_service = ChatService()
appointment_service = AppointmentService()
vector_service = VectorStoreService()

# Thiết lập secret key
app.secret_key = os.urandom(24)  # Tạo một secret key ngẫu nhiên

# Routes
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/chat")
def chat_page():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    response = chat_service.get_response(msg)
    return str(response["answer"])

@app.route("/get-available-slots", methods=["POST"])
def get_available_slots():
    """API lấy danh sách các khung giờ còn trống cho một ngày cụ thể."""
    date = request.form.get("date")
    if not date:
        return jsonify({"error": "Date is required"}), 400
    slots = appointment_service.get_available_slots(date)
    return jsonify({"slots": slots})

@app.route('/book', methods=['POST'])
def book_appointment():
    try:
        appointment_data = {
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
            flash('Appointment booked successfully!', 'success')
        else:
            flash(result['message'], 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route("/admin/appointments")
def admin_appointments():
    result = appointment_service.get_all_appointments()
    return render_template("admin_appointments.html", appointments=result['appointments'])

if __name__ == '__main__':
    try:
        app.run(host="0.0.0.0", port=8080, debug=True)
    finally:
        appointment_service.close()
