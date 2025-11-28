from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path
from typing import Any

from flask import Blueprint, current_app, jsonify, request, url_for, abort
from uuid import uuid4
import secrets
from PIL import Image
from sqlalchemy import or_

from ..extensions import db
from ..models import Painting, User
from ..schemas import PaintingSchema
from ..utils.storage import (
    StorageError,
    delete_file,
    download_image_stream,
    save_image_file,
    save_remote_image,
)
from ..utils.thumbnails import generate_thumbnail

paintings_bp = Blueprint("paintings", __name__)
painting_schema = PaintingSchema()


def _build_urls(painting: Painting) -> dict[str, Any]:
    payload = painting_schema.dump(painting)
    # include basic user info for gallery display
    payload["user"] = {"id": painting.user.id, "username": painting.user.username}
    payload["image_url"] = url_for(
        "media.serve_image", filename=painting.filename, _external=True
    )
    payload["format"] = painting.format
    if painting.thumbnail:
        payload["thumbnail_url"] = url_for(
            "media.serve_thumbnail",
            filename=painting.thumbnail,
            _external=True,
        )
    return payload


@paintings_bp.post("")
def create_painting():
    form = request.form.to_dict()
    file = request.files.get("image")
    user_id = form.get("user_id")
    desired_format = form.get("format")
    remote_url = form.get("image_url")

    # If no user_id provided or invalid, create a temporary anonymous user so
    # uploads still persist and can be associated with a name in the gallery.
    if not file and not remote_url:
        return {"error": "Provide an image file or image_url"}, 400

    user = None
    if user_id and user_id.isdigit():
        user = db.session.get(User, int(user_id))

    if not user:
        anon_name = f"anon_{uuid4().hex[:8]}"
        anon = User(username=anon_name, email=None)
        # set a random password hash so required field is satisfied
        anon.set_password(secrets.token_hex(16))
        db.session.add(anon)
        db.session.commit()
        user = anon

    image_dir = current_app.config["IMAGE_DIR"]
    thumb_dir = current_app.config["THUMBNAIL_DIR"]
    max_thumb = current_app.config["THUMBNAIL_SIZE"]

    try:
        if file:
            rel_path, abs_path, width, height, fmt = save_image_file(
                file, image_dir, desired_format=desired_format
            )
        else:
            rel_path, abs_path, width, height, fmt = save_remote_image(
                remote_url, image_dir, desired_format=desired_format
            )
        thumb_rel, _ = generate_thumbnail(abs_path, thumb_dir, max_size=max_thumb)
    except StorageError as exc:
        current_app.logger.exception("Failed to store image")
        return {"error": str(exc)}, 500

    painting = Painting(
        user_id=user.id,
        title=form.get("title"),
        filename=rel_path,
        thumbnail=thumb_rel,
        width=width,
        height=height,
        format=fmt,
        tools_used=form.get("tools_used"),
        tags=form.get("tags"),
        folder=form.get("folder"),
    )
    db.session.add(painting)
    db.session.commit()
    return _build_urls(painting), 201


@paintings_bp.get("")
def list_paintings():
    query = Painting.query
    user_id = request.args.get("user_id", type=int)
    search = request.args.get("q")
    folder = request.args.get("folder")
    tag = request.args.get("tag")
    image_format = request.args.get("format")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get(
        "per_page",
        default=current_app.config["RESULTS_PER_PAGE"],
        type=int,
    )

    if user_id:
        query = query.filter(Painting.user_id == user_id)
    if folder:
        query = query.filter(Painting.folder == folder)
    if image_format:
        query = query.filter(Painting.format == image_format.upper())
    if tag:
        query = query.filter(Painting.tags.ilike(f"%{tag}%"))
    if search:
        search_term = f"%{search}%"
        clauses = [Painting.title.ilike(search_term)]
        if search.isdigit():
            clauses.append(Painting.id == int(search))
        query = query.filter(or_(*clauses))

    pagination = query.order_by(Painting.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = [_build_urls(item) for item in pagination.items]
    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }


@paintings_bp.get("/<int:painting_id>")
def get_painting(painting_id: int):
    painting = db.session.get(Painting, painting_id)
    if not painting:
        abort(404)
    return _build_urls(painting)


@paintings_bp.put("/<int:painting_id>")
def update_painting(painting_id: int):
    painting = db.session.get(Painting, painting_id)
    if not painting:
        abort(404)
    payload = (
        request.form.to_dict()
        if request.content_type and "multipart" in request.content_type
        else request.json
        or {}
    )
    file = request.files.get("image") if request.files else None
    desired_format = payload.get("format")
    remote_url = payload.get("image_url")

    for field in ("title", "tools_used", "tags", "folder"):
        if field in payload:
            setattr(painting, field, payload[field])

    if file or remote_url:
        image_dir = current_app.config["IMAGE_DIR"]
        thumb_dir = current_app.config["THUMBNAIL_DIR"]
        max_thumb = current_app.config["THUMBNAIL_SIZE"]
        try:
            if file:
                rel_path, abs_path, width, height, fmt = save_image_file(
                    file, image_dir, desired_format=desired_format
                )
            else:
                rel_path, abs_path, width, height, fmt = save_remote_image(
                    remote_url, image_dir, desired_format=desired_format
                )
            thumb_rel, _ = generate_thumbnail(abs_path, thumb_dir, max_size=max_thumb)
            delete_file(Path(image_dir) / painting.filename)
            delete_file(Path(thumb_dir) / Path(painting.thumbnail or "").name)
            painting.filename = rel_path
            painting.thumbnail = thumb_rel
            painting.width = width
            painting.height = height
            painting.format = fmt
        except StorageError as exc:
            current_app.logger.exception("Failed to update image")
            return {"error": str(exc)}, 500

    if desired_format and not (file or remote_url):
        painting.format = desired_format.upper()

    db.session.commit()
    return _build_urls(painting)


@paintings_bp.delete("/<int:painting_id>")
def delete_painting(painting_id: int):
    painting = db.session.get(Painting, painting_id)
    if not painting:
        abort(404)
    image_dir = current_app.config["IMAGE_DIR"]
    thumb_dir = current_app.config["THUMBNAIL_DIR"]
    db.session.delete(painting)
    db.session.commit()

    try:
        delete_file(Path(image_dir) / painting.filename)
        if painting.thumbnail:
            delete_file(Path(thumb_dir) / Path(painting.thumbnail).name)
    except StorageError:
        current_app.logger.warning("Failed to remove painting files", exc_info=True)

    return {"status": "deleted"}


@paintings_bp.post("/import-url")
def import_from_url():
    payload = request.get_json() or {}
    url = payload.get("image_url")
    desired_format = payload.get("format")
    if not url:
        return {"error": "image_url is required"}, 400

    try:
        stream, _ = download_image_stream(url)
        buffer = stream.read()
        image = Image.open(BytesIO(buffer))
    except StorageError as exc:
        return {"error": str(exc)}, 400
    except Exception:
        return {"error": "Invalid remote image"}, 400

    fmt = (desired_format or image.format or "PNG").upper()
    if fmt == "JPEG":
        image = image.convert("RGB")
    else:
        image = image.convert("RGBA")
    output = BytesIO()
    image.save(output, format=fmt)
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    mime = "jpeg" if fmt == "JPEG" else fmt.lower()
    return {
        "data_url": f"data:image/{mime};base64,{encoded}",
        "width": image.width,
        "height": image.height,
        "format": fmt,
    }


@paintings_bp.post("/import-url/save")
def import_and_save():
    """Download a remote image and persist it as a Painting record.

    This endpoint takes JSON: `image_url` (required), optional `format`,
    optional `user_id`, and optional metadata like `title`, `tags`, `folder`.
    If `user_id` is missing or invalid an anonymous user will be created.
    """
    payload = request.get_json() or {}
    url = payload.get("image_url")
    desired_format = payload.get("format")
    user_id = payload.get("user_id")

    if not url:
        return {"error": "image_url is required"}, 400

    user = None
    if user_id and str(user_id).isdigit():
        user = db.session.get(User, int(user_id))

    if not user:
        # create an anonymous owner so uploaded images are associated
        from uuid import uuid4
        import secrets

        anon_name = f"anon_{uuid4().hex[:8]}"
        anon = User(username=anon_name, email=None)
        anon.set_password(secrets.token_hex(16))
        db.session.add(anon)
        db.session.commit()
        user = anon

    image_dir = current_app.config["IMAGE_DIR"]
    thumb_dir = current_app.config["THUMBNAIL_DIR"]
    max_thumb = current_app.config["THUMBNAIL_SIZE"]

    try:
        rel_path, abs_path, width, height, fmt = save_remote_image(
            url, image_dir, desired_format=desired_format
        )
        thumb_rel, _ = generate_thumbnail(abs_path, thumb_dir, max_size=max_thumb)
    except StorageError as exc:
        current_app.logger.exception("Failed to store remote image")
        return {"error": str(exc)}, 500

    painting = Painting(
        user_id=user.id,
        title=payload.get("title"),
        filename=rel_path,
        thumbnail=thumb_rel,
        width=width,
        height=height,
        format=fmt,
        tools_used=payload.get("tools_used"),
        tags=payload.get("tags"),
        folder=payload.get("folder"),
    )
    db.session.add(painting)
    db.session.commit()
    return _build_urls(painting), 201


