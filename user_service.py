from flask import Flask, request, jsonify

app = Flask(__name__)

# Тимчасові дані (користувачі)
users = {}

# Реєстрація
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get("email")
    if email in users:
        return jsonify({"error": "User already exists"}), 400
    users[email] = {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "phone": data.get("phone"),
        "password": data.get("password")
    }
    return jsonify({"message": "User registered successfully"}), 201

# Вхід
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    user = users.get(email)
    if not user or user.get("password") != password:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({"message": "Login successful"}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
