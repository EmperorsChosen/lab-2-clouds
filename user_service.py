from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Налаштування підключення до бази даних PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_user:12345@localhost:5432/parcels_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель для зберігання користувачів
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), default="user")  # Роль: "user" або "admin"

# Ініціалізація бази даних
with app.app_context():
    db.create_all()

# Реєстрація
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get("email")
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    new_user = User(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        email=email,
        phone=data.get("phone"),
        password=data.get("password"),
        role="admin" if data.get("is_admin") else "user"
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201



# Вхід
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email, password=password).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "role": user.role
    }), 200

# Отримати інформацію про користувача
@app.route('/get-user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


