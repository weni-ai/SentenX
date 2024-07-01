import os

import sentry_sdk

from langchain.vectorstores import VectorStore
from langchain.docstore.document import Document

from app.store import IStorage


class ElasticsearchVectorStoreIndex(IStorage):
    def __init__(self, vectorstore: VectorStore, score=1.55):
        self.vectorstore = vectorstore
        self.score = score

    def save(self, doc: Document) -> list[str]:
        texts = [doc.page_content]
        metadatas = [doc.metadata]
        return self.vectorstore.add_texts(texts, metadatas)

    def save_batch(self, documents: list[Document]) -> list[str]:
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.vectorstore.add_texts(texts, metadatas)

    def search(self, search: str, filter=None, threshold=0.1) -> list[Document]:
        sr = self.vectorstore.similarity_search_with_score(
            query=search, k=15, filter=filter
        )
        return [doc[0] for doc in sr if doc[1] > threshold]

    def query_search(self, search_filter: dict) -> list[dict]:
        match_field: str = list(search_filter.keys())[0]
        match_value: str = search_filter[match_field]
        term_field = list(search_filter.keys())[1]
        term_value = search_filter[term_field]
        query_script = {
            "bool": {
                "must": [{"match": {match_field: match_value}}],
                "filter": {"terms": {term_field: term_value}},
            }
        }
        try:
            self.vectorstore.client.indices.get(index=self.vectorstore.index_name)
        except Exception:
            return []

        source = ["metadata"]
        response = self.vectorstore.client.search(
            index=self.vectorstore.index_name, query=query_script, source=source
        )
        hits = [hit for hit in response["hits"]["hits"]]
        return hits

    def delete(self, ids: list[str] = []) -> bool:
        return self.vectorstore.delete(ids)


class ContentBaseElasticsearchVectorStoreIndex(ElasticsearchVectorStoreIndex):

    def save(self, docs: list[Document]) -> list[str]:
        index = os.environ.get("INDEX_CONTENTBASES_NAME", "content_bases")
        res = self.vectorstore.from_documents(
            docs,
            self.vectorstore.embeddings,
            es_url=os.environ.get("ELASTICSEARCH_URL"),
            index_name=index,
            bulk_kwargs={
                "chunk_size": os.environ.get("DEFAULT_CHUNK_SIZE", 75),
                "max_chunk_bytes": 200000000
            }
        )
        return res

    def query_search(self, search_filter: dict) -> list[dict]:
        match_field: str = list(search_filter.keys())[0]
        match_value: str = search_filter[match_field]

        query_script = {
            "bool": {
                "must": [{"match": {match_field: match_value}}],
            }
        }
        try:
            self.vectorstore.client.indices.get(index=self.vectorstore.index_name)
        except Exception:
            return []

        source = ["metadata"]
        response = self.vectorstore.client.search(
            index=self.vectorstore.index_name, query=query_script, source=source
        )
        hits = [hit for hit in response["hits"]["hits"]]
        return hits

    def search_delete(self, search_filter: dict, scroll_id: str = None) -> tuple[str, dict]:

        if scroll_id:
            response = self.vectorstore.client.scroll(scroll_id=scroll_id, scroll='2m')
            scroll_id = response["_scroll_id"]
            hits = [hit for hit in response["hits"]["hits"]]
            return scroll_id, hits

        match_field1: str = list(search_filter.keys())[0]
        match_value1: str = search_filter[match_field1]
        match_field2 = list(search_filter.keys())[1]
        match_value2 = search_filter[match_field2]

        query_script = {
            "bool": {
                "must": [
                    {"match": {match_field1: match_value1}},
                    {"match": {match_field2: match_value2}}
                ],
            }
        }

        try:
            self.vectorstore.client.indices.get(index=self.vectorstore.index_name)
        except Exception:
            return []

        source = ["metadata"]

        response = self.vectorstore.client.search(
            index=self.vectorstore.index_name,
            query=query_script,
            source=source,
            scroll="2m",
            size=100,
        )
        scroll_id = response["_scroll_id"]
        hits = [hit for hit in response["hits"]["hits"]]
        return scroll_id, hits

    def search(self, search: str, filter=None, threshold=0.1) -> list[Document]:
        content_base_uuid = filter.get("content_base_uuid")
        q = {"bool": {"filter": [{"term": {"metadata.content_base_uuid.keyword": content_base_uuid}}]}}


        docs = self.vectorstore.similarity_search_with_score(query=search, k=5, filter=q)
        return [doc[0] for doc in docs if doc[1] > threshold]

    def delete(self, ids: list[str] = []) -> bool:
        return self.vectorstore.delete(ids)

    def save_doc_content(self, full_content, content_base_uuid, filename, file_uuid) -> None:
        elasticsearch_doc = {
            "content": full_content,
            "content_base_uuid": content_base_uuid,
            "filename": filename,
            "file_uuid":file_uuid
        }
        es_client = self.vectorstore.client
        res = es_client.index(index="content_base_documents", body=elasticsearch_doc)
        return

    def search_doc_content(self, file_uuid: str, content_base_uuid: str) -> str:
        query = {
            "bool": {
                "filter": [
                    { "term": { "file_uuid.keyword": file_uuid}},
                    { "term": { "content_base_uuid.keyword": content_base_uuid}}
                ]
            }
        }
        es_client = self.vectorstore.client
        try:
            res = es_client.search(index="content_base_documents", query=query)
            hits = res["hits"]["hits"]

            if len(hits) > 0:
                doc = hits[0]
                return doc.get("_source").get("content")
            return ""
        except Exception as e:
            sentry_sdk.capture_message(f"{e}")
            return ""

    def check_if_doc_was_embedded_document(self, file_uuid: str, content_base_uuid: str) -> bool:
        query = {
            "bool": {
                "filter": [
                    { "term": { "metadata.file_uuid.keyword": file_uuid}},
                    { "term": { "metadata.content_base_uuid.keyword": content_base_uuid}}
                ]
            }
        }
        es_client = self.vectorstore.client
        try:
            res = es_client.search(index=self.vectorstore.index_name, query=query)
            hits = res["hits"].get("total").get("value")

            return hits > 0
        except Exception as e:
            sentry_sdk.capture_message(f"{e}")
            return False
