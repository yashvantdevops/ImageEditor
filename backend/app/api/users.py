from __future__ import annotations

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import User
from ..schemas import UserCreateSchema, UserSchema

users_bp = Blueprint("users", __name__)
user_schema = UserSchema()
user_create_schema = UserCreateSchema()


@users_bp.post("")
def create_user():
    payload = request.get_json() or {}
    try:
        data = user_create_schema.load(payload)
    except ValidationError as err:
        return {"errors": err.messages}, 400
    user = User(username=data["username"], email=data.get("email"))
    user.set_password(data["password"])
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Username or email already exists"}, 409
    return user_schema.dump(user), 201


@users_bp.get("")
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify(user_schema.dump(users, many=True))

