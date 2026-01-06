"""File entity to DTO mappers"""

from typing import List

from contexts.file_management.domain.entities.file import File

from ..read_models import FileListItemReadModel, FileReadModel
from .file_dto import FileDownloadResponseDTO, FileListResponseDTO, FileResponseDTO


class FileMapper:
    """File domain entity to DTO mapper"""

    @staticmethod
    def to_read_model(file: File) -> FileReadModel:
        """
        Convert file entity to read model.

        Used by command handlers to return consistent read models.

        Args:
            file: File domain entity

        Returns:
            FileReadModel
        """
        return FileReadModel(
            id=file.id,
            name=file.name,
            original_name=file.original_name,
            path=file.path.value,
            size=file.size.bytes,
            mime_type=file.mime_type.value,
            owner_id=file.owner_id,
            description=file.description,
            is_public=file.is_public,
            download_count=file.download_count,
            shared_with=file.shared_with,
            is_deleted=file.is_deleted,
            created_at=file.created_at,
            updated_at=file.updated_at,
        )

    @staticmethod
    def to_list_item_read_model(file: File) -> FileListItemReadModel:
        """
        Convert file entity to list item read model.

        Args:
            file: File domain entity

        Returns:
            FileListItemReadModel
        """
        return FileListItemReadModel(
            id=file.id,
            original_name=file.original_name,
            size=file.size.bytes,
            mime_type=file.mime_type.value,
            is_public=file.is_public,
            download_count=file.download_count,
            owner_id=file.owner_id,
            created_at=file.created_at,
        )

    @staticmethod
    def to_response_dto(file: File) -> FileResponseDTO:
        """Convert file entity to response DTO"""
        return FileResponseDTO(
            id=file.id,
            name=file.name,
            original_name=file.original_name,
            path=file.path.value,
            size=file.size.bytes,
            size_human=file.size.human_readable(),
            mime_type=file.mime_type.value,
            owner_id=file.owner_id,
            description=file.description,
            is_public=file.is_public,
            download_count=file.download_count,
            shared_with=file.shared_with,
            file_extension=file.file_extension,
            is_image=file.is_image,
            is_document=file.is_document,
            created_at=file.created_at,
            updated_at=file.updated_at,
        )

    @staticmethod
    def to_list_dto(file: File) -> FileListResponseDTO:
        """Convert file entity to list DTO"""
        return FileListResponseDTO(
            id=file.id,
            original_name=file.original_name,
            size_human=file.size.human_readable(),
            mime_type=file.mime_type.value,
            is_public=file.is_public,
            download_count=file.download_count,
            created_at=file.created_at,
        )

    @staticmethod
    def to_list_dtos(files: List[File]) -> List[FileListResponseDTO]:
        """Convert list of file entities to list DTOs"""
        return [FileMapper.to_list_dto(file) for file in files]

    @staticmethod
    def to_download_dto(file: File) -> FileDownloadResponseDTO:
        """Convert file entity to download DTO"""
        return FileDownloadResponseDTO(
            id=file.id,
            name=file.name,
            original_name=file.original_name,
            path=file.path.value,
            mime_type=file.mime_type.value,
            size=file.size.bytes,
        )
