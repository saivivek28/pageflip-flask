from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS, cross_origin
from bson.objectid import ObjectId
import os
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"], supports_credentials=True)

bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = "pass"
jwt = JWTManager(app)

# MongoDB
client = MongoClient("mongodb+srv://saiviveknakirikanti:sD8knh1LnpcXyb0C@cluster0.0f18ktb.mongodb.net/")
db = client["flaskdb"]
collection = db["user"]
books_collection = client['mylibrary']["books"]

def serialize_user(u: dict) -> dict:
    if not u: return {}
    return {
        "_id": str(u.get("_id")),
        "name": u.get("name"),
        "email": u.get("email"),
        "phone": u.get("phone"),
        "address": u.get("address"),
        "profileImageUrl": u.get("profileImageUrl", ""),
        "role": u.get("role", "user")
    }

def serialize_book(book: dict) -> dict:
    if not book: return {}
    return {
        "_id": str(book.get("_id")),
        "bookId": str(book.get("_id")),  # Add bookId for frontend compatibility
        "title": book.get("title"),
        "author": book.get("author"),
        "description": book.get("description"),
        "genre": book.get("genre"),
        "coverImage": book.get("coverImage"),
        "pdfUrl": book.get("pdfUrl", ""),
        "pages": book.get("pages", 0),
        "publishedDate": book.get("publishedDate"),
        "isbn": book.get("isbn"),
        "rating": book.get("rating", 0),
        "totalRatings": book.get("totalRatings", 0),
        "type": book.get("type", "ebook"),
        "priceBuy": book.get("priceBuy", 299),
        "priceRent": book.get("priceRent", 99),
        "stock": book.get("stock", 10),
        "format": book.get("format", "PDF")
    }

# Register
@app.route('/register', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def register():
    data = request.get_json() or {}
    for f in ['name','email','password']:
        if not data.get(f): return jsonify({'error': f'{f} is required'}), 400
    if collection.find_one({'email': data['email']}):
        return jsonify({'error': 'User already exists'}), 409
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    collection.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed,
        'phone': data.get('phone',''),
        'address': data.get('address',''),
        'profileImageUrl': '',
        'role': 'user'  # Default role
    })
    return jsonify({'message': 'User registered successfully'}), 201

# Login
@app.route('/login', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def login():
    data = request.get_json() or {}
    email, password = data.get('email'), data.get('password')
    if not email or not password: return jsonify({'error':'Email and password required'}), 400
    user = collection.find_one({'email': email})
    if not user: return jsonify({'error':'User not found'}), 404
    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error':'Incorrect password'}), 401
    token = create_access_token(identity={'name': user['name'], 'email': user['email'], 'role': user.get('role', 'user')})
    return jsonify({
        'message':'Login successful',
        'token':token,
        '_id':str(user['_id']),
        'role': user.get('role', 'user')
    }), 200

# Admin Login
@app.route('/admin/login', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def admin_login():
    data = request.get_json() or {}
    email, password = data.get('email'), data.get('password')
    if not email or not password: return jsonify({'error':'Email and password required'}), 400
    
    # Check if user exists and is admin
    user = collection.find_one({'email': email, 'role': 'admin'})
    if not user: return jsonify({'error':'Admin not found'}), 404
    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error':'Incorrect password'}), 401
    
    token = create_access_token(identity=str(user['_id']))
    return jsonify({
        'message':'Admin login successful',
        'token':token,
        '_id':str(user['_id']),
        'role': 'admin'
    }), 200

# Create admin user (run this once to create first admin)
@app.route('/create-admin', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def create_admin():
    data = request.get_json() or {}
    for f in ['name','email','password']:
        if not data.get(f): return jsonify({'error': f'{f} is required'}), 400
    if collection.find_one({'email': data['email']}):
        return jsonify({'error': 'User already exists'}), 409
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    collection.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed,
        'phone': data.get('phone',''),
        'address': data.get('address',''),
        'profileImageUrl': '',
        'role': 'admin'
    })
    return jsonify({'message': 'Admin created successfully'}), 201

# Users
@app.route('/users', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def get_users():
    return jsonify([serialize_user(u) for u in collection.find()]), 200

@app.route('/user/<id>', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def get_user(id):
    try: oid = ObjectId(id)
    except: return jsonify({'error':'Invalid user id'}), 400
    user = collection.find_one({"_id": oid})
    if not user: return jsonify({'error':'User not found'}), 404
    return jsonify(serialize_user(user)), 200

# Update profile fields
@app.route('/user/<id>', methods=['PUT'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def update_user(id):
    try: oid = ObjectId(id)
    except: return jsonify({'error':'Invalid user id'}), 400
    data = request.get_json() or {}
    allowed = {k: data.get(k) for k in ['name','email','phone','address','profileImageUrl']}
    update_doc = {k:v for k,v in allowed.items() if v is not None}
    if update_doc:
        collection.update_one({'_id': oid}, {'$set': update_doc})
    user = collection.find_one({'_id': oid})
    return jsonify(serialize_user(user)), 200

# Profile Image Upload
@app.route('/user/<id>/profile-image', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def upload_profile_image(id):
    try: 
        oid = ObjectId(id)
    except: 
        return jsonify({'error':'Invalid user id'}), 400
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG, GIF allowed'}), 400
    
    # Convert image to base64 for storage in MongoDB
    image_data = file.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    image_url = f"data:image/{file.filename.rsplit('.', 1)[1].lower()};base64,{base64_image}"
    
    # Update user's profile image URL
    collection.update_one({'_id': oid}, {'$set': {'profileImageUrl': image_url}})
    
    return jsonify({'url': image_url, 'message': 'Profile image uploaded successfully'}), 200

# Profile Image Delete
@app.route('/user/<id>/profile-image', methods=['DELETE'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def delete_profile_image(id):
    try: 
        oid = ObjectId(id)
    except: 
        return jsonify({'error':'Invalid user id'}), 400
    
    # Remove profile image URL from user
    collection.update_one({'_id': oid}, {'$set': {'profileImageUrl': ''}})
    
    return jsonify({'message': 'Profile image removed successfully'}), 200

# Books
@app.route('/books', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def get_books():
    books = list(books_collection.find())
    return jsonify([serialize_book(book) for book in books]), 200

@app.route('/books/<id>', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def get_book(id):
    try: oid = ObjectId(id)
    except: return jsonify({'error':'Invalid book id'}), 400
    book = books_collection.find_one({"_id": oid})
    if not book: return jsonify({'error':'Book not found'}), 404
    return jsonify(serialize_book(book)), 200

# Rate a book (user)
@app.route('/books/<id>/rate', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def rate_book(id):
    try:
        oid = ObjectId(id)
    except:
        return jsonify({'error': 'Invalid book id'}), 400

    data = request.get_json() or {}
    try:
        rating_value = float(data.get('rating', 0))
    except:
        return jsonify({'error': 'Rating must be a number'}), 400

    if rating_value < 1 or rating_value > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    book = books_collection.find_one({'_id': oid})
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    current_avg = float(book.get('rating', 0) or 0)
    current_count = int(book.get('totalRatings', 0) or 0)

    # Compute new average without storing sum
    new_count = current_count + 1
    new_avg = (current_avg * current_count + rating_value) / new_count

    books_collection.update_one({'_id': oid}, {'$set': {
        'rating': round(new_avg, 2),
        'totalRatings': new_count
    }})

    updated = books_collection.find_one({'_id': oid})
    return jsonify(serialize_book(updated)), 200

# Admin-only book management
@app.route('/admin/books', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
@jwt_required()
def add_book():
    user_id = get_jwt_identity()
    user = collection.find_one({'_id': ObjectId(user_id)})
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
        'pdfUrl': data.get('pdfUrl', ''),
        'pages': data.get('pages', 0),
        'publishedDate': data.get('publishedDate', ''),
        'isbn': data.get('isbn', ''),
        'rating': 0,
        'totalRatings': 0,
        'type': data.get('type', 'ebook'),
        'priceBuy': data.get('priceBuy', 299),
        'priceRent': data.get('priceRent', 99),
        'stock': data.get('stock', 10),
        'format': data.get('format', 'PDF')
    }
    
    result = books_collection.insert_one(book_data)
    book_data['_id'] = str(result.inserted_id)
    return jsonify(serialize_book(book_data)), 201

@app.route('/admin/books/<id>', methods=['PUT'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
@jwt_required()
def update_book(id):
    user_id = get_jwt_identity()
    user = collection.find_one({'_id': ObjectId(user_id)})
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try: oid = ObjectId(id)
    except: return jsonify({'error':'Invalid book id'}), 400
    
    data = request.get_json() or {}
    allowed_fields = ['title', 'author', 'description', 'genre', 'coverImage', 'pdfUrl', 'pages', 'publishedDate', 'isbn', 'type', 'priceBuy', 'priceRent', 'stock', 'format']
    update_doc = {k: data[k] for k in allowed_fields if k in data}
    
    if update_doc:
        books_collection.update_one({'_id': oid}, {'$set': update_doc})
    
    book = books_collection.find_one({'_id': oid})
    if not book: return jsonify({'error':'Book not found'}), 404
    return jsonify(serialize_book(book)), 200

@app.route('/admin/books/<id>', methods=['DELETE'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
@jwt_required()
def delete_book(id):
    user_id = get_jwt_identity()
    user = collection.find_one({'_id': ObjectId(user_id)})
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try: oid = ObjectId(id)
    except: return jsonify({'error':'Invalid book id'}), 400
    
    result = books_collection.delete_one({'_id': oid})
    if result.deleted_count == 0:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify({'message': 'Book deleted successfully'}), 200

# Admin dashboard stats
@app.route('/admin/stats', methods=['GET'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
@jwt_required()
def get_admin_stats():
    user_id = get_jwt_identity()
    user = collection.find_one({'_id': ObjectId(user_id)})
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Count regular users (excluding admins)
        total_users = collection.count_documents({'role': {'$ne': 'admin'}})
        
        # Count all books
        total_books = books_collection.count_documents({})
        
        # Count admins
        total_admins = collection.count_documents({'role': 'admin'})
        
        # Get recent activity counts (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Count recent users (if createdAt field exists)
        recent_users = collection.count_documents({
            'role': {'$ne': 'admin'},
            'createdAt': {'$gte': thirty_days_ago}
        })
        
        # Calculate average rating across all books
        pipeline = [
            {'$group': {'_id': None, 'avgRating': {'$avg': '$rating'}}}
        ]
        avg_rating_result = list(books_collection.aggregate(pipeline))
        avg_rating = round(avg_rating_result[0]['avgRating'], 1) if avg_rating_result and avg_rating_result[0]['avgRating'] else 0
        
        return jsonify({
            'totalUsers': total_users,
            'totalBooks': total_books,
            'totalAdmins': total_admins,
            'recentUsers': recent_users,
            'averageRating': avg_rating,
            'lastUpdated': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error getting admin stats: {e}")
        return jsonify({'error': 'Failed to retrieve stats'}), 500

if __name__ == '__main__':
    app.run(debug=True)
