from langchain.docstore.document import Document

from app.handlers.products import Product
from app.indexer import IDocumentIndexer
from app.store import IStorage
from typing import List
from uuid import UUID


class ContentBaseIndexer(IDocumentIndexer):
    def __init__(self, storage: IStorage):
        self.storage = storage

    def index(self, texts: List, metadatas: dict):
        results = self._search_docs_by_content_base_uuid(
            content_base_uuid=metadatas.get('content_base_uuid')
        )
        ids = []
        if len(results) > 0:
            ids = [item["_id"] for item in results]
            self.storage.delete(ids=ids)

        docs = [
            Document(page_content=text.lower(), metadata=metadatas)
            for text in texts
        ]

        return self.storage.save(docs)

    def index_batch(self):
        raise NotImplementedError

    def search(self, search, filter=None, threshold=0.1) -> list[Product]:
        matched_responses = self.storage.search(search, filter, threshold)
        return [doc.page_content for doc in matched_responses]

    def _search_docs_by_content_base_uuid(self, content_base_uuid: UUID):
        search_filter = {
            "metadata.content_base_uuid": content_base_uuid
        }
        return self.storage.query_search(search_filter)

    def delete(self, content_base_uuid: UUID, filename: str):
        search_filter = {
            "metadata.content_base_uuid": content_base_uuid,
            "metadata.source": filename,
        }

        scroll_id, results = self.storage.search_delete(search_filter)
        ids = []

        while len(results) > 0:
            ids += [item["_id"] for item in results]
            scroll_id, results = self.storage.search_delete(search_filter, scroll_id)
        
        if ids:
            self.storage.delete(ids=ids)

    def delete_batch(self):
        raise NotImplementedError
