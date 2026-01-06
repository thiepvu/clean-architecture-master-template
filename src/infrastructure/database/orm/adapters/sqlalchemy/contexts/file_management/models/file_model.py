"""File SQLAlchemy models"""

from typing import List
from uuid import UUID

from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from infrastructure.database.orm.adapters.sqlalchemy.shared.base_model import register_module_base

# Register Base for file module (uses default schema from registry)
# No config service needed - schema comes from DEFAULT_MODULE_SCHEMAS
module_base = register_module_base("file")


class FileModel(module_base.BaseModel):  # type: ignore[name-defined]
    """File ORM model"""

    __tablename__ = "files"

    name = Column(String(255), nullable=False, unique=True, index=True, comment="Internal filename")
    original_name = Column(String(255), nullable=False, comment="Original filename")
    path = Column(String(500), nullable=False, comment="Storage path")
    size = Column(Integer, nullable=False, comment="File size in bytes")
    mime_type = Column(String(100), nullable=False, index=True, comment="MIME type")
    owner_id = Column(PGUUID(as_uuid=True), nullable=False, index=True, comment="Owner user ID")
    description = Column(Text, nullable=True, comment="File description")
    is_public = Column(Boolean, default=False, nullable=False, index=True, comment="Public access")
    download_count = Column(Integer, default=0, nullable=False, comment="Download count")
    shared_with: "Column[List[UUID]]" = Column(
        ARRAY(PGUUID(as_uuid=True)), default=list, nullable=False, comment="Shared with user IDs"
    )

    def __repr__(self) -> str:
        return f"<File(id={self.id}, name={self.original_name})>"
