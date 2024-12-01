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

    # Перевірка, чи авторизований користувач
    if not is_user_authenticated(data.get("user_email")):
        return jsonify({"error": "Unauthorized"}), 401

    # Додавання посилки
    new_parcel = Parcel(
        user_email=data.get("user_email"),
        description=data.get("description"),
        status=data.get("status")
    )
    db.session.add(new_parcel)
    db.session.commit()
    return jsonify({"message": "Parcel request created", "parcel": {
        "id": new_parcel.id,
        "user_email": new_parcel.user_email,
        "description": new_parcel.description,
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
    user_email = request.args.get("email")

    # Перевірка, чи авторизований користувач
    if not is_user_authenticated(user_email):
        return jsonify({"error": "Unauthorized"}), 401

    # Фільтрування посилок
    user_parcels = Parcel.query.filter_by(user_email=user_email).all()
    return jsonify([{
        "id": parcel.id,
        "user_email": parcel.user_email,
        "description": parcel.description,
        "status": parcel.status
    } for parcel in user_parcels])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)



