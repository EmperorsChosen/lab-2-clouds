import requests
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Налаштування підключення до бази даних PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_user:12345@localhost:5432/parcels_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для зберігання посилок
class Parcel(db.Model):
    __tablename__ = 'parcels'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False) 
    description = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)  
    insurance_price = db.Column(db.Float, nullable=False)  
    status = db.Column(db.String(50), nullable=False, default="Pending")

# Ініціалізація бази даних
with app.app_context():
    db.create_all()

# Перевірка, чи авторизований користувач
def is_user_authenticated(email):
    response = requests.post("http://localhost:5001/login", json={"email": email, "password": "test"})
    return response.status_code == 200

# Додати запит на відправлення посилки
@app.route('/parcels', methods=['POST'])
def add_parcel():
    data = request.json
    print(f"Received data: {data}")  # Додано для відлагодження

    # Додавання посилки
    new_parcel = Parcel(
        user_id=data.get("user_id"),
        description=data.get("description"),
        destination=data.get("destination"),
        insurance_price=data.get("insurance_price"),
        status="Pending"
    )
    db.session.add(new_parcel)
    db.session.commit()
    print(f"Parcel added: {new_parcel.id}")  # Логування успішного додавання
    return jsonify({"message": "Parcel request created", "parcel": {
        "id": new_parcel.id,
        "user_id": new_parcel.user_id,
        "description": new_parcel.description,
        "destination": new_parcel.destination,
        "insurance_price": new_parcel.insurance_price,
        "status": new_parcel.status
    }}), 201



# Відстежити статус посилки
@app.route('/parcels/<int:parcel_id>', methods=['GET'])
def track_parcel(parcel_id):
    parcel = Parcel.query.get(parcel_id)
    if not parcel:
        return jsonify({"error": "Parcel not found"}), 404
    return jsonify({
        "id": parcel.id,
        "user_email": parcel.user_email,
        "description": parcel.description,
        "status": parcel.status
    })

# Переглянути всі посилки (клієнт)
@app.route('/my-parcels', methods=['GET'])
def get_user_parcels():
    user_id = request.args.get("user_id")

    # Перевірка, чи авторизований користувач
    if not is_user_authenticated_by_id(user_id):
        return jsonify({"error": "Unauthorized"}), 401

    # Фільтрування посилок
    user_parcels = Parcel.query.filter_by(user_id=user_id).all()

    # Отримання імені користувача через `users_service`
    user_info = requests.get(f"http://localhost:5001/get-user/{user_id}").json()

    return jsonify([{
        "id": parcel.id,
        "first_name": user_info.get("first_name"),
        "last_name": user_info.get("last_name"),
        "description": parcel.description,
        "destination": parcel.destination,
        "insurance_price": parcel.insurance_price,
        "status": parcel.status
    } for parcel in user_parcels])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)



