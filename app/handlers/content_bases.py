from fastapi import APIRouter
from fastapi.logger import logger
from pydantic import BaseModel

from app.handlers import IDocumentHandler
from app.indexer import IDocumentIndexer
from app.downloaders import IFileDownloader

from app.celery import index_file_data, celery


class ContentBaseIndexRequest(BaseModel):
    file: str
    filename: str
    extension_file: str
    task_uuid: str
    content_base: str


class ContentBaseIndexResponse(BaseModel):
    file: str
    filename: str
    task_uuid: str


class ContentBaseHandler(IDocumentHandler):
    def __init__(self, content_base_indexer: IDocumentIndexer):
        self.content_base_indexer = content_base_indexer
        self.router = APIRouter()
        self.router.add_api_route(
            "/content_base/index", endpoint=self.index, methods=["PUT"]
        )

    def index(self, request: ContentBaseIndexRequest):

        content_base = request.__dict__
        task = index_file_data.delay(content_base)

        return ContentBaseIndexResponse(
            file=request.file,
            filename=request.filename,
            task_uuid=task.id,
        )

    def batch_index(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def delete_batch(self):
        raise NotImplementedError

    def search(self):
        raise NotImplementedError
