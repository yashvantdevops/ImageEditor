from __future__ import annotations

from flask import Blueprint, current_app, request
from itsdangerous import URLSafeTimedSerializer
from marshmallow import ValidationError

from ..models import User
from ..schemas import LoginSchema, UserSchema

auth_bp = Blueprint("auth", __name__)
login_schema = LoginSchema()
user_schema = UserSchema()


def _serializer() -> URLSafeTimedSerializer:
    secret = current_app.config["SECRET_KEY"]
    return URLSafeTimedSerializer(secret_key=secret, salt="canvas3t-auth")


@auth_bp.post("/login")
def login():
    payload = request.get_json() or {}
    try:
        data = login_schema.load(payload)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return {"error": "Invalid credentials"}, 401

    token = _serializer().dumps({"user_id": user.id})
    return {"token": token, "user": user_schema.dump(user)}

