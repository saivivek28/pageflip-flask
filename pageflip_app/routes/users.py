from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from bson.objectid import ObjectId
from ..db import get_collections
from ..utils import serialize_user

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def get_users():
    users_col, _ = get_collections()
    return jsonify([serialize_user(u) for u in users_col.find()]), 200


@users_bp.route('/user/<id>', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def get_user(id):
    users_col, _ = get_collections()
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({'error': 'Invalid user id'}), 400
    user = users_col.find_one({'_id': oid})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(serialize_user(user)), 200


@users_bp.route('/user/<id>', methods=['PUT'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def update_user(id):
    users_col, _ = get_collections()
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({'error': 'Invalid user id'}), 400
    data = request.get_json() or {}
    allowed = {k: data.get(k) for k in ['name', 'email', 'phone', 'address', 'profileImageUrl']}
    update_doc = {k: v for k, v in allowed.items() if v is not None}
    if update_doc:
        users_col.update_one({'_id': oid}, {'$set': update_doc})
    user = users_col.find_one({'_id': oid})
    return jsonify(serialize_user(user)), 200


@users_bp.route('/user/<id>/profile-image', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def upload_profile_image(id):
    from base64 import b64encode

    users_col, _ = get_collections()
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({'error': 'Invalid user id'}), 400

    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF allowed'}), 400

    image_data = file.read()
    base64_image = b64encode(image_data).decode('utf-8')
    image_url = f"data:image/{file.filename.rsplit('.', 1)[1].lower()};base64,{base64_image}"

    users_col.update_one({'_id': oid}, {'$set': {'profileImageUrl': image_url}})
    return jsonify({'url': image_url, 'message': 'Profile image uploaded successfully'}), 200


@users_bp.route('/user/<id>/profile-image', methods=['DELETE'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def delete_profile_image(id):
    users_col, _ = get_collections()
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({'error': 'Invalid user id'}), 400

    users_col.update_one({'_id': oid}, {'$set': {'profileImageUrl': ''}})
    return jsonify({'message': 'Profile image removed successfully'}), 200
