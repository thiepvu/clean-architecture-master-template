"""
File Management Commands and Command Handlers.

Commands represent intentions to change state (write operations).
Each command has exactly one handler.
"""

from .delete_file import DeleteFileCommand, DeleteFileHandler
from .share_file import ShareFileCommand, ShareFileHandler
from .update_file import UpdateFileCommand, UpdateFileHandler
from .upload_file import UploadFileCommand, UploadFileHandler

__all__ = [
    # Commands
    "UploadFileCommand",
    "UpdateFileCommand",
    "DeleteFileCommand",
    "ShareFileCommand",
    # Handlers
    "UploadFileHandler",
    "UpdateFileHandler",
    "DeleteFileHandler",
    "ShareFileHandler",
]
