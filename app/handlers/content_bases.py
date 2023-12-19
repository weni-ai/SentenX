from fastapi import APIRouter, Header
from pydantic import BaseModel

from app.handlers import IDocumentHandler
from app.indexer import IDocumentIndexer

from app.celery import index_file_data
from typing import List
from typing import Annotated
from app.handlers.authorizations import token_verification

import requests, os


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


class ContentBaseSearchRequest(BaseModel):
    search: str
    filter: dict[str, str] = None
    threshold: float = 1.5


class ContentBaseSearchResponse(BaseModel):
    response: List[str]


class ContentBaseHandler(IDocumentHandler):
    def __init__(self, content_base_indexer: IDocumentIndexer):
        self.content_base_indexer = content_base_indexer
        self.router = APIRouter()
        self.router.add_api_route(
            "/content_base/index", endpoint=self.index, methods=["PUT"]
        )
        self.router.add_api_route(
            "/content_base/search", endpoint=self.search, methods=["GET"]
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

    def delete(self):
        raise NotImplementedError

    def delete_batch(self):
        raise NotImplementedError

    def search(self, request: ContentBaseSearchRequest, Authorization: Annotated[str | None, Header()] = None):
        token_verification(Authorization)
        response = self.content_base_indexer.search(
            search=request.search.lower(),
            threshold=request.threshold,
            filter=request.filter
        )
        return ContentBaseSearchResponse(response=response)


class NexusRESTClient:
    token = os.environ.get("NEXUS_AI_TOKEN")
    base_url = os.environ.get("NEXUS_AI_URL")

    def __init__(self) -> None:
        self.headers = {
            'Authorization': self.token,
            'Content-Type': "application/json"
        }

    def index_succedded(self, task_succeded: bool, nexus_task_uuid: str) -> None:
        endpoint = f'{self.base_url}/api/v1/content-base-file'
        data = { 
            "status": int(task_succeded),
            "task_uuid": nexus_task_uuid,
        }
        response = requests.patch(url=endpoint, data=data, headers=self.headers)
        response.raise_for_status()
