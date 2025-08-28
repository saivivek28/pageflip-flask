from bson.objectid import ObjectId

def serialize_user(u: dict) -> dict:
    if not u:
        return {}
    return {
        "_id": str(u.get("_id")),
        "name": u.get("name"),
        "email": u.get("email"),
        "phone": u.get("phone"),
        "address": u.get("address"),
        "profileImageUrl": u.get("profileImageUrl", ""),
        "role": u.get("role", "user"),
    }


def serialize_book(book: dict) -> dict:
    if not book:
        return {}
    _id = book.get("_id")
    _id_str = str(_id) if _id is not None else None
    return {
        "_id": _id_str,
        "bookId": _id_str,
        "title": book.get("title"),
        "author": book.get("author"),
        "description": book.get("description"),
        "genre": book.get("genre"),
        "coverImage": book.get("coverImage"),
        "pages": book.get("pages", 0),
        "publishedDate": book.get("publishedDate"),
        "isbn": book.get("isbn"),
        "rating": book.get("rating", 0),
        "totalRatings": book.get("totalRatings", 0),
        "type": book.get("type", "ebook"),
        "priceBuy": book.get("priceBuy", 299),
        "priceRent": book.get("priceRent", 99),
        "stock": book.get("stock", 10),
        "format": book.get("format", "PDF"),
    }
