from langchain.docstore.document import Document

from app.handlers.products import Product
from app.indexer import IDocumentIndexer
from app.store import IStorage
from typing import List
from uuid import UUID
from app.rerank import rerank_chunks


class ContentBaseIndexer(IDocumentIndexer):
    def __init__(self, storage: IStorage):
        self.storage = storage

    def index_documents(self, docs: List[Document]):
        BATCH_SIZE: int = 500
        docs_size: int = len(docs)

        file_uuid = docs[0].metadata["file_uuid"]
        content_base_uuid = docs[0].metadata["content_base_uuid"]

        results = self._search_docs_by_content_base_uuid(
            content_base_uuid=content_base_uuid,
            file_uuid=file_uuid,
        )
        ids = []
        if len(results) > 0:
            ids = [item["_id"] for item in results]
            self.storage.delete(ids=ids)

        for i in range(0, docs_size, BATCH_SIZE):
            self.storage.save(docs[i:BATCH_SIZE + i])

        return

    def index(self, texts: List, metadatas: dict):
        results = self._search_docs_by_content_base_uuid(
            content_base_uuid=metadatas.get('content_base_uuid')
        )
        ids = []
        if len(results) > 0:
            ids = [item["_id"] for item in results]
            self.storage.delete(ids=ids)

        docs = [
            Document(page_content=text, metadata=metadatas)
            for text in texts
        ]

        return self.storage.save(docs)

    def index_batch(self):
        raise NotImplementedError

    def search(self, search, filter=None, threshold=0.1) -> list[Product]:
        matched_responses = self.storage.search(search, filter, threshold)

        seen = set()
        return_list = []

        for doc in matched_responses:
            full_page = doc.metadata.get("full_page")

            if full_page not in seen:
                seen.add(full_page)
                return_list.append({
                    "text": full_page,
                    "full_page": full_page,
                    "filename": doc.metadata.get("filename"),
                    "file_uuid": doc.metadata.get("file_uuid"),
                })

        chunks = rerank_chunks(search, return_list, 0.4, 5)

        return chunks

    def _search_docs_by_content_base_uuid(
        self,
        content_base_uuid: UUID,
        file_uuid: str = None
    ):
        search_filter = {
            "metadata.content_base_uuid": content_base_uuid
        }
        if file_uuid:
            search_filter.update({"metadata.file_uuid": file_uuid})
        return self.storage.query_search(search_filter)

    def delete(self, content_base_uuid: UUID, filename: str, file_uuid: str):
        search_filter = {
            "metadata.content_base_uuid": content_base_uuid,
            "metadata.file_uuid": file_uuid,
        }

        if filename:
            search_filter.update({"metadata.source": filename})

        scroll_id, results = self.storage.search_delete(search_filter)
        ids = []

        while len(results) > 0:
            ids += [item["_id"] for item in results]
            scroll_id, results = self.storage.search_delete(
                search_filter,
                scroll_id
            )

        if ids:
            self.storage.delete(ids=ids)

    def index_doc_content(self, full_content: str, content_base_uuid: UUID, filename: str, file_uuid: str):
        self.storage.save_doc_content(
            full_content=full_content,
            content_base_uuid=content_base_uuid,
            filename=filename,
            file_uuid=file_uuid
        )

    def delete_batch(self):
        raise NotImplementedError

    def search_document_content(self, file_uuid: str, content_base_uuid: str) -> str:
        return self.storage.search_doc_content(file_uuid, content_base_uuid)

    def check_if_doc_was_embedded_document(self, file_uuid: str, content_base_uuid: str) -> bool:
        return self.storage.check_if_doc_was_embedded_document(file_uuid, content_base_uuid)
