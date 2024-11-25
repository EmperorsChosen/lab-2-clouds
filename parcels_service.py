import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Тимчасові дані (посилки)
parcels = []
parcel_id = 1

# Перевірка, чи авторизований користувач
def is_user_authenticated(email):
    response = requests.post("http://127.0.0.1:5001/login", json={"email": email, "password": "test"})
    return response.status_code == 200

# Додати запит на відправлення посилки
@app.route('/parcels', methods=['POST'])
def add_parcel():
    global parcel_id
    data = request.json

    # Перевірка, чи авторизований користувач
    if not is_user_authenticated(data.get("user_email")):
        return jsonify({"error": "Unauthorized"}), 401

    # Додавання посилки
    data["id"] = parcel_id
    parcels.append(data)
    parcel_id += 1
    return jsonify({"message": "Parcel request created", "parcel": data}), 201

# Відстежити статус посилки
@app.route('/parcels/<int:parcel_id>', methods=['GET'])
def track_parcel(parcel_id):
    parcel = next((p for p in parcels if p["id"] == parcel_id), None)
    if not parcel:
        return jsonify({"error": "Parcel not found"}), 404
    return jsonify(parcel)

# Переглянути всі посилки (клієнт)
@app.route('/my-parcels', methods=['GET'])
def get_user_parcels():
    user_email = request.args.get("email")

    # Перевірка, чи авторизований користувач
    if not is_user_authenticated(user_email):
        return jsonify({"error": "Unauthorized"}), 401

    # Фільтрування посилок
    user_parcels = [p for p in parcels if p["user_email"] == user_email]
    return jsonify(user_parcels)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
