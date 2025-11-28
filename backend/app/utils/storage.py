from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Tuple
from uuid import uuid4

import requests
from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class StorageError(RuntimeError):
    pass


SUPPORTED_FORMATS = {
    "PNG": "png",
    "JPEG": "jpg",
    "JPG": "jpg",
    "WEBP": "webp",
}


def _safe_name(filename: str, extension: str) -> str:
    base = Path(filename).stem or "canvas3t"
    cleaned = secure_filename(base)
    return f"{uuid4().hex}_{cleaned}.{extension}"


def _resolve_format(desired: str | None, detected: str | None) -> tuple[str, str]:
    target = (desired or detected or "PNG").upper()
    if target not in SUPPORTED_FORMATS:
        raise StorageError(f"Unsupported format: {target}")
    return target, SUPPORTED_FORMATS[target]


def persist_image_stream(
    stream: BinaryIO,
    original_name: str,
    image_dir: str,
    *,
    desired_format: str | None = None,
) -> tuple[str, Path, int, int, str]:
    base_dir = Path(image_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

    buffer = BytesIO(stream.read())
    buffer.seek(0)

    try:
        image = Image.open(buffer)
    except Exception as exc:
        raise StorageError("Invalid image payload") from exc

    fmt, ext = _resolve_format(desired_format, image.format)
    filename = _safe_name(original_name, ext)
    target_path = base_dir / filename

    if fmt == "JPEG":
        image = image.convert("RGB")
    else:
        image = image.convert("RGBA")

    image.save(target_path, format=fmt)
    return (
        str(target_path.relative_to(base_dir)),
        target_path,
        image.width,
        image.height,
        fmt,
    )


def save_image_file(
    file_storage: FileStorage,
    image_dir: str,
    *,
    desired_format: str | None = None,
) -> tuple[str, Path, int, int, str]:
    if not file_storage or not file_storage.filename:
        raise StorageError("Missing image file")

    file_storage.stream.seek(0)
    return persist_image_stream(
        file_storage.stream,
        file_storage.filename,
        image_dir,
        desired_format=desired_format,
    )


def download_image_stream(url: str) -> tuple[BytesIO, str]:
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover
        raise StorageError("Unable to download remote image") from exc

    filename = Path(url.split("?")[0]).name or "remote.png"
    stream = BytesIO(response.content)
    stream.seek(0)
    return stream, filename


def save_remote_image(
    url: str, image_dir: str, *, desired_format: str | None = None
) -> tuple[str, Path, int, int, str]:
    stream, filename = download_image_stream(url)
    return persist_image_stream(
        stream, filename, image_dir, desired_format=desired_format
    )


def delete_file(path: str | Path) -> None:
    try:
        Path(path).unlink(missing_ok=True)
    except OSError as exc:  # pragma: no cover - best effort cleanup
        raise StorageError(f"Unable to delete file: {path}") from exc

