from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from bson.objectid import ObjectId
from ..db import get_collections
from ..utils import serialize_book

books_bp = Blueprint('books', __name__)


@books_bp.route('/books', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def get_books():
    _, books_col = get_collections()
    books = list(books_col.find())
    return jsonify([serialize_book(book) for book in books]), 200


@books_bp.route('/books/<id>', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def get_book(id):
    _, books_col = get_collections()
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({'error': 'Invalid book id'}), 400
    book = books_col.find_one({'_id': oid})
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(serialize_book(book)), 200


@books_bp.route('/books/<id>/rate', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def rate_book(id):
    _, books_col = get_collections()
    try:
        oid = ObjectId(id)
    except Exception:
        return jsonify({'error': 'Invalid book id'}), 400

    data = request.get_json() or {}
    try:
        rating_value = float(data.get('rating', 0))
    except Exception:
        return jsonify({'error': 'Rating must be a number'}), 400

    if rating_value < 1 or rating_value > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    book = books_col.find_one({'_id': oid})
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    current_avg = float(book.get('rating', 0) or 0)
    current_count = int(book.get('totalRatings', 0) or 0)

    new_count = current_count + 1
    new_avg = (current_avg * current_count + rating_value) / new_count

    books_col.update_one({'_id': oid}, {'$set': {'rating': round(new_avg, 2), 'totalRatings': new_count}})

    updated = books_col.find_one({'_id': oid})
    return jsonify(serialize_book(updated)), 200
