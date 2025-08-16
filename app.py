# from flask import Flask, request, jsonify
# from flask_bcrypt import Bcrypt
# from pymongo import MongoClient
# from flask_jwt_extended import JWTManager, create_access_token
# from flask_cors import CORS, cross_origin
# from schemes import User_schema
# from bson.objectid import ObjectId
# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": ["http://localhost:4200"]}}, supports_credentials=True )
# bcrypt = Bcrypt(app)

# user_schema = User_schema()
# users_schema = User_schema(many=True)

# # ✅ Allow only Angular frontend
# # , resources={r"/*": {"origins": ["http://localhost:4200"]}}, supports_credentials=True


# # JWT secret key
# app.config['JWT_SECRET_KEY'] = "pass"
# jwt = JWTManager(app)

# # MongoDB connection
# client = MongoClient("mongodb+srv://saiviveknakirikanti:sD8knh1LnpcXyb0C@cluster0.0f18ktb.mongodb.net/")
# db = client["flaskdb"]
# collection = db["user"]

# def serialize_user(user):
#     return {
#         "_id": str(user['_id']),
#         "name": user['name'],
#         "email": user['email']
#     }

# @app.route('/register', methods=['POST', 'OPTIONS'])
# @cross_origin(origin='http://localhost:4200', supports_credentials=True)
# def register():
#     # Handle preflight CORS request
#     if request.method == "OPTIONS":
#         return '', 204  # 204 = No Content

#     data = request.get_json()
#     name = data.get('name')
#     email = data.get('email')
#     password = data.get('password')

#     # Validate fields
#     errors = user_schema.validate(data)
#     if errors:
#         print("Validation errors:", errors)  # Debug
#         return jsonify(errors), 400


#     # Check if user exists
#     if collection.find_one({'email': email}):
#         return jsonify({'error': 'User already exists'}), 409

#     # Hash the password
#     hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#     new_user = {
#         'name': name,
#         'email': email,
#         'password': hashed_password
#     }

#     # Save to DB
#     collection.insert_one(new_user)

#     return jsonify({'message': 'User registered successfully'}), 201



# @app.route('/login', methods=['POST', 'OPTIONS'])
# @cross_origin(origin='http://localhost:4200', supports_credentials=True)
# def login():
#     if request.method == "OPTIONS":
#         return jsonify("OK"), 200  # Preflight CORS response

#     data = request.json
#     email = data.get('email')
#     password = data.get('password')

#     if not email or not password:
#         return jsonify({'error': 'Email and password required'}), 400

#     user = collection.find_one({'email': email})
#     if not user:
#         return jsonify({'error': 'User not found'}), 404

#     stored_hash = user['password']

#     if not bcrypt.check_password_hash(stored_hash, password):
#         return jsonify({'error': 'Incorrect password'}), 401

#     token = create_access_token(identity={'name': user['name'], 'email': user['email']})
#     return jsonify({
#         'message': 'Login successful',
#         'token': token,
#         '_id': str(user['_id'])
#     }), 200





# @app.route('/users', methods=['GET'])
# @cross_origin(origin='http://localhost:4200', supports_credentials=True)
# def get_users():
#     users = collection.find()
#     return jsonify(users_schema.dump(users)), 200


# @app.route('/user/<id>')
# def get_user(id
#     user = collection.find_one({"_id": ObjectId(id)})
#     return jsonify(user_schema.dump(user)), 200


# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS, cross_origin
from schemes import User_schema
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4200"]}}, supports_credentials=True)

bcrypt = Bcrypt(app)
user_schema = User_schema()
users_schema = User_schema(many=True)

# JWT secret key
app.config['JWT_SECRET_KEY'] = "pass"
jwt = JWTManager(app)

# MongoDB connection
client = MongoClient("mongodb+srv://saiviveknakirikanti:sD8knh1LnpcXyb0C@cluster0.0f18ktb.mongodb.net/")
db = client["flaskdb"]
collection = db["user"]

# -------------------- REGISTER --------------------
@app.route('/register', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def register():
    data = request.get_json()

    # Validate with marshmallow
    errors = user_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Check duplicate
    if collection.find_one({'email': data['email']}):
        return jsonify({'error': 'User already exists'}), 409

    # Hash password
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    collection.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password
    })

    return jsonify({'message': 'User registered successfully'}), 201


# -------------------- LOGIN --------------------
@app.route('/login', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def login():
    data = request.json

    # Validate
    errors = user_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Find user
    user = collection.find_one({'email': data.get('email')})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check password
    if not bcrypt.check_password_hash(user['password'], data.get('password')):
        return jsonify({'error': 'Incorrect password'}), 401

    # JWT Token
    token = create_access_token(identity={'name': user['name'], 'email': user['email']})
    return jsonify({
        'message': 'Login successful',
        'token': token,
        '_id': str(user['_id'])
    }), 200


# -------------------- GET ALL USERS --------------------
@app.route('/users', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def get_users():
    users = collection.find()
    return jsonify(users_schema.dump(users)), 200


# -------------------- GET USER BY ID --------------------
@app.route('/user/<id>', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def get_user(id):
    user = collection.find_one({"_id": ObjectId(id)})
    return jsonify(user_schema.dump(user)), 200


if __name__ == '__main__':
    app.run(debug=True)
