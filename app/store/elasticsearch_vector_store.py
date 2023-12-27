from langchain.vectorstores import VectorStore
from langchain.docstore.document import Document

from app.store import IStorage

from fastapi.logger import logger
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

    def save(self, docs: list[Document])-> list[str]:
        res = self.vectorstore.from_documents(docs, self.vectorstore.embeddings, index_name="content_bases")
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
        except Exception as e:
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
        except Exception as e:
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
        docs = self.vectorstore.similarity_search_with_score(query=search, k=5, filter=filter)
        return [doc[0] for doc in docs if doc[1] > threshold]

    def delete(self, ids: list[str] = []) -> bool:
        return self.vectorstore.delete(ids)
