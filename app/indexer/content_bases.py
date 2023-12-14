from langchain.docstore.document import Document

from app.handlers.products import Product
from app.indexer import IDocumentIndexer
from app.store import IStorage
from typing import List
from uuid import UUID
from fastapi.logger import logger


class ContentBaseIndexer(IDocumentIndexer):
    def __init__(self, storage: IStorage):
        self.storage = storage

    def index(self, texts: List, metadatas: dict):
        results = self._search_products_by_content_base_uuid(
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

    def index_batch(self, catalog_id: str, products: list[Product]):
        raise NotImplementedError

    def search(self, search, filter=None, threshold=0.1) -> list[Product]:
        matched_responses = self.storage.search(search, filter, threshold)
        return [doc.page_content for doc in matched_responses]

    def _search_products_by_content_base_uuid(self, content_base_uuid: UUID):
        search_filter = {
            "metadata.content_base_uuid": content_base_uuid
        }
        return self.storage.query_search(search_filter)

    def delete(self, catalog_id, product_retailer_id):
        raise NotImplementedError

    def delete_batch(self, catalog_id, product_retailer_ids):
        raise NotImplementedError