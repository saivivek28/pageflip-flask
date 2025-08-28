from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from bson.objectid import ObjectId
from ..extensions import bcrypt, jwt
from flask_jwt_extended import create_access_token
from ..db import get_collections

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def register():
    users_col, _ = get_collections()
    data = request.get_json() or {}
    for f in ['name', 'email', 'password']:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400
    if users_col.find_one({'email': data['email']}):
        return jsonify({'error': 'User already exists'}), 409
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    users_col.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed,
        'phone': data.get('phone', ''),
        'address': data.get('address', ''),
        'profileImageUrl': '',
        'role': 'user'
    })
    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def login():
    users_col, _ = get_collections()
    data = request.get_json() or {}
    email, password = data.get('email'), data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    user = users_col.find_one({'email': email})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error': 'Incorrect password'}), 401
    token = create_access_token(identity={'name': user['name'], 'email': user['email'], 'role': user.get('role', 'user')})
    return jsonify({'message': 'Login successful', 'token': token, '_id': str(user['_id']), 'role': user.get('role', 'user')}), 200


@auth_bp.route('/admin/login', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def admin_login():
    users_col, _ = get_collections()
    data = request.get_json() or {}
    email, password = data.get('email'), data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    user = users_col.find_one({'email': email, 'role': 'admin'})
    if not user:
        return jsonify({'error': 'Admin not found'}), 404
    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error': 'Incorrect password'}), 401
    token = create_access_token(identity=str(user['_id']))
    return jsonify({'message': 'Admin login successful', 'token': token, '_id': str(user['_id']), 'role': 'admin'}), 200


@auth_bp.route('/create-admin', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def create_admin():
    users_col, _ = get_collections()
    data = request.get_json() or {}
    for f in ['name', 'email', 'password']:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400
    if users_col.find_one({'email': data['email']}):
        return jsonify({'error': 'User already exists'}), 409
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    users_col.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed,
        'phone': data.get('phone', ''),
        'address': data.get('address', ''),
        'profileImageUrl': '',
        'role': 'admin'
    })
    return jsonify({'message': 'Admin created successfully'}), 201
