from fastapi import APIRouter, Header
from pydantic import BaseModel

from app.handlers import IDocumentHandler
from app.indexer import IDocumentIndexer

from app.celery import index_file_data
from typing import List
from typing import Annotated
from app.handlers.authorizations import token_verification


class ContentBaseIndexRequest(BaseModel):
    file: str
    filename: str
    file_uuid: str
    extension_file: str
    task_uuid: str
    content_base: str
    load_type: str = None


class ContentBaseIndexResponse(BaseModel):
    file: str
    filename: str
    task_uuid: str


class ContentBaseSearchRequest(BaseModel):
    search: str
    filter: dict[str, str] = None
    threshold: float = 1.5


class ContentBaseSearchResponse(BaseModel):
    response: List[dict]


class ContentBaseDeleteRequest(BaseModel):
    filename: str
    content_base: str
    file_uuid: str


class ContentBaseDeleteResponse(BaseModel):
    deleted: bool


class ContentBaseSearchDocumentRequest(BaseModel):
    file_uuid: str
    content_base_uuid: str


class ContentBaseSearchDocumentResponse(BaseModel):
    content: str


class ContentBaseHandler(IDocumentHandler):
    def __init__(self, content_base_indexer: IDocumentIndexer):
        self.content_base_indexer = content_base_indexer
        self.router = APIRouter()
        self.router.add_api_route(
            "/content_base/index", endpoint=self.index, methods=["PUT"]
        )
        self.router.add_api_route(
            "/content_base/search", endpoint=self.search, methods=["POST"]
        )
        self.router.add_api_route(
            "/content_base/search-document", endpoint=self.search_document_content, methods=["POST"]
        )
        self.router.add_api_route(
            "/content_base/delete", endpoint=self.delete, methods=["DELETE"]
        )

    def index(self, request: ContentBaseIndexRequest, Authorization: Annotated[str | None, Header()] = None):
        token_verification(Authorization)
        content_base = request.__dict__
        task = index_file_data.delay(content_base)

        return ContentBaseIndexResponse(
            file=request.file,
            filename=request.filename,
            task_uuid=task.id,
        )

    def batch_index(self):
        raise NotImplementedError

    def delete(
        self,
        request: ContentBaseDeleteRequest,
        Authorization: Annotated[str | None, Header()] = None
    ):
        token_verification(Authorization)
        self.content_base_indexer.delete(
            request.content_base,
            request.filename,
            request.file_uuid,
        )
        return ContentBaseDeleteResponse(deleted=True)

    def delete_batch(self):
        raise NotImplementedError

    def search(
        self,
        request: ContentBaseSearchRequest,
        Authorization: Annotated[str | None, Header()] = None
    ):
        token_verification(Authorization)
        response = self.content_base_indexer.search(
            search=request.search,
            threshold=request.threshold,
            filter=request.filter
        )
        return ContentBaseSearchResponse(response=response)

    def search_document_content(
        self,
        request: ContentBaseSearchDocumentRequest,
        Authorization: Annotated[str | None, Header()] = None
    ):
        token_verification(Authorization)
        response = self.content_base_indexer.search_document_content(
            file_uuid=request.file_uuid,
            content_base_uuid=request.content_base_uuid
        )
        return ContentBaseSearchDocumentResponse(content=response)
