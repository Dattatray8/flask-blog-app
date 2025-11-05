from flask import jsonify, request, Blueprint
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from bson.objectid import ObjectId
from datetime import datetime
from utils.db import db

blogs_bp = Blueprint("blogs", __name__, url_prefix="/api/v1/blogs")


@blogs_bp.route("/", methods=["POST"])
@jwt_required()
def create_blog():
    user_id = get_jwt_identity()
    print(request.cookies, "hi")
    data = request.get_json()
    if not data or "title" not in data or "content" not in data:
        return jsonify({"error": "Title and content are required"}), 400
    blog_data = {
        "title": data["title"],
        "content": data["content"],
        "author_id": ObjectId(user_id),
        "created_at": datetime.now(),
    }
    try:
        blog = db.blogs.insert_one(blog_data)
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"blogs": blog.inserted_id}},
        )
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    return jsonify({"message": "Blog created successfully"}), 201


@blogs_bp.route("/", methods=["GET"])
def get_blogs():
    page = request.args.get("page", type=int, default=1)
    skip = (page - 1) * 10
    blogs = []
    try:
        for blog in db.blogs.find().skip(skip).limit(10).sort("created_at", -1):
            author = db.users.find_one({"_id": blog["author_id"]})
            blogs.append(
                {
                    "id": str(blog["_id"]),
                    "title": blog["title"],
                    "content": blog["content"],
                    "author": author["username"] if author else "Unknown",
                }
            )
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

    return jsonify(blogs), 200


@blogs_bp.route("/<id>", methods=["GET"])
@jwt_required()
def get_blog(id):
    try:
        blog = db.blogs.find_one({"_id": ObjectId(id)})
        if not blog:
            return jsonify({"error": "Blog not found"}), 404
        author = db.users.find_one({"_id": blog["author_id"]})
        return (
            jsonify(
                {
                    "id": str(blog["_id"]),
                    "title": blog["title"],
                    "content": blog["content"],
                    "author": author["username"] if author else "Unknown",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500


@blogs_bp.route("/<id>", methods=["PUT"])
@jwt_required()
def update_blog(id):
    try:
        user_id = get_jwt_identity()
        user = db.users.find_one({"_id": ObjectId(user_id)})
        data = request.get_json()
        blog = db.blogs.find_one({"_id": ObjectId(id)})

        if not blog:
            return jsonify({"error": "Blog not found"}), 404
        if not user or user["_id"] != blog["author_id"]:
            return jsonify({"error": "You are not authorized to update this blog"}), 401
        if not data or "title" not in data or "content" not in data:
            return jsonify({"error": "Title and content are required"}), 400

        db.blogs.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "title": data["title"],
                    "content": data["content"],
                    "updated_at": datetime.now(),
                }
            },
        )
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    return jsonify({"message": "Blog updated successfully"}), 200


@blogs_bp.route("/<id>", methods=["DELETE"])
@jwt_required()
def delete_blog(id):
    try:
        user_id = get_jwt_identity()
        user = db.users.find_one({"_id": ObjectId(user_id)})
        blog = db.blogs.find_one({"_id": ObjectId(id)})
        if not blog:
            return jsonify({"error": "Blog not found"}), 404
        if not user or user["_id"] != blog["author_id"]:
            return jsonify({"error": "You are not authorized to delete this blog"}), 401

        db.blogs.delete_one({"_id": ObjectId(id)})
        db.users.update_one(
            {"_id": blog["author_id"]},
            {"$pull": {"blogs": ObjectId(id)}},
        )
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    return jsonify({"message": "Blog deleted successfully"}), 200


@blogs_bp.route("/search", methods=["GET"])
def search_blogs():
    query = request.args.get("q", "")
    blogs = []
    try:
        for blog in db.blogs.find({"title": {"$regex": query, "$options": "i"}}).sort(
            "created_at", -1
        ):
            author = db.users.find_one({"_id": blog["author_id"]})
            blogs.append(
                {
                    "id": str(blog["_id"]),
                    "title": blog["title"],
                    "content": blog["content"],
                    "author": author["username"] if author else "Unknown",
                }
            )
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

    return jsonify(blogs or []), 200
