from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
)
from bson.objectid import ObjectId
from utils.db import db
from utils.auth import bcrypt

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@users_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if (
        not data
        or "username" not in data
        or "password" not in data
        or "email" not in data
    ):
        return jsonify({"error": "All fields are required"}), 400
    isUserExist = db.users.find_one({"email": data["email"]})
    if isUserExist:
        return jsonify({"error": "User already exists"}), 400
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    data["password"] = hashed_password
    try:
        user = db.users.insert_one(data)
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    access_token = create_access_token(identity=str(user.inserted_id))
    resp = jsonify({"message": "User signed up successfully"})
    set_access_cookies(resp, access_token)
    return resp, 201


@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "password" not in data or "email" not in data:
        return jsonify({"error": "All fields are required"}), 400
    try:
        isUserExist = db.users.find_one({"email": data["email"]})
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    if not isUserExist:
        return jsonify({"error": "User not found"}), 404
    if not bcrypt.check_password_hash(isUserExist["password"], data["password"]):
        return jsonify({"error": "Invalid password"}), 401
    access_token = create_access_token(identity=str(isUserExist["_id"]))
    resp = jsonify({"message": "User logged in successfully"})
    set_access_cookies(resp, access_token)
    return resp, 200


@users_bp.route("/logout", methods=["GET"])
@jwt_required()
def logout():
    resp = jsonify({"message": "User logged out successfully"})
    unset_jwt_cookies(resp)
    return resp, 200


@users_bp.route("/current", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        blogs = db.blogs.find({"author_id": ObjectId(user_id)}).sort("created_at", -1)
    except Exception as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    if not user:
        return jsonify({"error": "User not found"}), 404
    return (
        jsonify(
            {
                "username": user["username"],
                "blogs": [
                    {
                        "id": str(blog["_id"]),
                        "title": blog["title"],
                        "content": blog["content"],
                    }
                    for blog in blogs
                ],
            }
        ),
        200,
    )
