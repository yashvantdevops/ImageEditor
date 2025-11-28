from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, current_app, send_from_directory

media_bp = Blueprint("media", __name__)


@media_bp.get("/images/<path:filename>")
def serve_image(filename: str):
    image_dir = current_app.config["IMAGE_DIR"]
    return send_from_directory(image_dir, filename)


@media_bp.get("/thumbnails/<path:filename>")
def serve_thumbnail(filename: str):
    thumb_dir = current_app.config["THUMBNAIL_DIR"]
    return send_from_directory(thumb_dir, filename)


@media_bp.get("/download/<path:filename>")
def download_image(filename: str):
    """Send image as an attachment so clients can download the original file."""
    image_dir = current_app.config["IMAGE_DIR"]
    return send_from_directory(image_dir, filename, as_attachment=True)

