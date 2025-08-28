from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..db import get_collections
from ..utils import serialize_book

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/books', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
@jwt_required()
def add_book():
    users_col, books_col = get_collections()
    user_id = get_jwt_identity()
    user = users_col.find_one({'_id': ObjectId(user_id)})
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json() or {}
    required_fields = ['title', 'author']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    book_data = {
        'title': data['title'],
        'author': data['author'],
        'description': data.get('description', ''),
        'genre': data.get('genre', ''),
        'coverImage': data.get('coverImage', ''),
        'pages': data.get('pages', 0),
        'publishedDate': data.get('publishedDate', ''),
        'isbn': data.get('isbn', ''),
        'rating': 0,
        'totalRatings': 0
    }

    result = books_col.insert_one(book_data)
    book_data['_id'] = result.inserted_id
    return jsonify(serialize_book(book_data)), 201


@admin_bp.route('/admin/books/<id>', methods=['PUT'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
@jwt_required()
def update_book(id):
    users_col, books_col = get_collections()
    user_id = get_jwt_identity()
    user = users_col.find_one({'_id': ObjectId(user_id)})
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({'error': 'Invalid book id'}), 400

    data = request.get_json() or {}
    allowed_fields = ['title', 'author', 'description', 'genre', 'coverImage', 'pages', 'publishedDate', 'isbn']
    update_doc = {k: data[k] for k in allowed_fields if k in data}

    if update_doc:
        books_col.update_one({'_id': oid}, {'$set': update_doc})

    book = books_col.find_one({'_id': oid})
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(serialize_book(book)), 200


@admin_bp.route('/admin/books/<id>', methods=['DELETE'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
@jwt_required()
def delete_book(id):
    users_col, books_col = get_collections()
    user_id = get_jwt_identity()
    user = users_col.find_one({'_id': ObjectId(user_id)})
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({'error': 'Invalid book id'}), 400

    result = books_col.delete_one({'_id': oid})
    if result.deleted_count == 0:
        return jsonify({'error': 'Book not found'}), 404

    return jsonify({'message': 'Book deleted successfully'}), 200


@admin_bp.route('/admin/stats', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
@jwt_required()
def get_admin_stats():
    users_col, books_col = get_collections()
    user_id = get_jwt_identity()
    user = users_col.find_one({'_id': ObjectId(user_id)})
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    try:
        total_users = users_col.count_documents({'role': {'$ne': 'admin'}})
        total_books = books_col.count_documents({})
        total_admins = users_col.count_documents({'role': 'admin'})

        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_users = users_col.count_documents({'role': {'$ne': 'admin'}, 'createdAt': {'$gte': thirty_days_ago}})

        pipeline = [{'$group': {'_id': None, 'avgRating': {'$avg': '$rating'}}}]
        avg_rating_result = list(books_col.aggregate(pipeline))
        avg_rating = round(avg_rating_result[0]['avgRating'], 1) if avg_rating_result and avg_rating_result[0]['avgRating'] else 0

        return jsonify({'totalUsers': total_users, 'totalBooks': total_books, 'totalAdmins': total_admins, 'recentUsers': recent_users, 'averageRating': avg_rating, 'lastUpdated': datetime.now().isoformat()}), 200
    except Exception as e:
        print(f"Error getting admin stats: {e}")
        return jsonify({'error': 'Failed to retrieve stats'}), 500
