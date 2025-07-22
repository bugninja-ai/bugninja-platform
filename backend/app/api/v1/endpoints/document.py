from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.endpoints.utils import COMMON_ERROR_RESPONSES, create_success_response
from app.db.base import get_db
from app.repo.document_repo import DocumentRepo
from app.repo.project_repo import ProjectRepo
from app.schemas.crud.document import CreateDocument, ResponseDocument

documents_router = APIRouter(prefix="/documents", tags=["Documents"])


@documents_router.post(
    "/",
    response_model=ResponseDocument,
    summary="Create Document",
    description="Create a new document with the provided data",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: create_success_response("Document created successfully", ResponseDocument),
        **COMMON_ERROR_RESPONSES,
    },
)
async def create_document(
    document_data: CreateDocument = Depends(),
    db_session: Session = Depends(get_db),
) -> ResponseDocument:
    """
    Create a new document with the specified name and content.

    This endpoint creates a new document in the system and returns the created document instance.
    The document will be associated with a specific project and can contain text content.
    """
    try:
        # Validate that the referenced project exists
        project = ProjectRepo.get_by_id(db=db_session, project_id=document_data.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {document_data.project_id} not found",
            )

        created_document = DocumentRepo.create(db=db_session, document_data=document_data)
        return ResponseDocument(
            id=created_document.id,
            project_id=created_document.project_id,
            created_at=created_document.created_at,
            updated_at=created_document.updated_at,
            name=created_document.name,
            content=created_document.content,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document: {str(e)}",
        )


@documents_router.get(
    "/{document_id:str}",
    response_model=ResponseDocument,
    summary="Get Document by ID",
    description="Retrieve a specific document by its ID",
    responses={
        200: create_success_response("Document retrieved successfully", ResponseDocument),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_document_by_id(
    document_id: str,
    db_session: Session = Depends(get_db),
) -> ResponseDocument:
    """
    Retrieve a specific document by its unique identifier.

    This endpoint returns detailed document information including content and metadata.
    """
    try:
        document = DocumentRepo.get_by_id(db=db_session, document_id=document_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )

        return ResponseDocument(
            id=document.id,
            project_id=document.project_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
            name=document.name,
            content=document.content,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}",
        )


@documents_router.get(
    "/project/{project_id:str}",
    response_model=List[ResponseDocument],
    summary="Get Documents by Project",
    description="Retrieve all documents for a specific project",
    responses={
        200: create_success_response("Project documents retrieved successfully", ResponseDocument),
        **COMMON_ERROR_RESPONSES,
    },
)
async def get_documents_by_project(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(get_db),
) -> List[ResponseDocument]:
    """
    Retrieve all documents for a specific project.

    This endpoint returns a paginated list of all documents associated with a particular project.
    Use skip and limit parameters for pagination control.
    """
    try:
        documents = DocumentRepo.get_by_project_id(
            db=db_session, project_id=project_id, skip=skip, limit=limit
        )
        return [
            ResponseDocument(
                id=doc.id,
                project_id=doc.project_id,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                name=doc.name,
                content=doc.content,
            )
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project documents: {str(e)}",
        )


@documents_router.delete(
    "/{document_id:str}",
    response_model=ResponseDocument,
    summary="Delete Document",
    description="Delete a document by its ID",
    responses={
        200: create_success_response("Document deleted successfully", ResponseDocument),
        **COMMON_ERROR_RESPONSES,
    },
)
async def delete_document(
    document_id: str,
    db_session: Session = Depends(get_db),
) -> ResponseDocument:
    """
    Delete a document from the system.

    This endpoint permanently removes a document and returns the deleted document information.
    """
    try:
        # First get the document to return it after deletion
        document = DocumentRepo.get_by_id(db=db_session, document_id=document_id)

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
            )

        # Delete the document
        success = DocumentRepo.delete(db=db_session, document_id=document_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete document with id {document_id}",
            )

        return ResponseDocument(
            id=document.id,
            project_id=document.project_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
            name=document.name,
            content=document.content,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}",
        )
