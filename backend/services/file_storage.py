"""
File-storage helpers for uploaded bank statements.

Uploaded files are stored under ``storage/uploads/{user_id}/`` so each
user has an isolated directory.  The module exposes simple, synchronous
helpers because FastAPI's ``UploadFile`` already buffers the request body.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

from backend.config import settings


def get_upload_path(user_id: int) -> Path:
    """Return (and ensure existence of) the upload directory for *user_id*.

    Args:
        user_id: The ID of the user whose directory is required.

    Returns:
        A ``Path`` pointing to ``<UPLOAD_DIR>/<user_id>/``.
    """
    path = Path(settings.UPLOAD_DIR) / str(user_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload(file: UploadFile, user_id: int) -> str:
    """Persist an uploaded file to disk.

    The file is saved with a timestamp prefix to avoid name collisions.

    Args:
        file: The ``UploadFile`` received from the FastAPI endpoint.
        user_id: Owner of the upload.

    Returns:
        The absolute path of the saved file as a string.

    Raises:
        ValueError: If the file has no filename.
    """
    if not file.filename:
        raise ValueError("Uploaded file has no filename.")

    dest_dir = get_upload_path(user_id)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{file.filename}"
    dest_path = dest_dir / safe_name

    # Write the file contents to disk.
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(dest_path.resolve())


def list_uploads(user_id: int) -> list[dict]:
    """List all previously uploaded files for *user_id*.

    Args:
        user_id: Owner of the uploads.

    Returns:
        A list of dicts with keys ``filename``, ``size_bytes``, ``uploaded_at``
        (ISO-format string derived from the file's modification time), and
        ``path`` (absolute path).
    """
    upload_dir = get_upload_path(user_id)
    files: list[dict] = []

    for entry in sorted(upload_dir.iterdir()):
        if entry.is_file():
            stat = entry.stat()
            files.append(
                {
                    "filename": entry.name,
                    "size_bytes": stat.st_size,
                    "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "path": str(entry.resolve()),
                }
            )

    return files
