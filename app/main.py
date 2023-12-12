from fastapi import FastAPI
from langchain.embeddings import SagemakerEndpointEmbeddings, HuggingFaceHubEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import ElasticVectorSearch, VectorStore

from app.handlers import IDocumentHandler
from app.handlers.products import ProductsHandler
from app.indexer import IDocumentIndexer
from app.indexer.products import ProductsIndexer
from app.store.elasticsearch_vector_store import ElasticsearchVectorStoreIndex, ContentBaseElasticsearchVectorStoreIndex
from app.config import AppConfig
from app.util import ContentHandler


from app.handlers.content_bases import ContentBaseHandler
from app.indexer.content_bases import ContentBaseIndexer
from app.embedders.embedders import SagemakerEndpointEmbeddingsKeys


class App:
    api: FastAPI
    config: AppConfig
    embeddings: Embeddings
    vectorstore: VectorStore
    products_handler: IDocumentHandler
    products_indexer: IDocumentIndexer

    def __init__(self, config: AppConfig):
        self.config = config
        if config.embedding_type == "huggingface":
            self.embeddings = HuggingFaceHubEmbeddings(
                repo_id=config.huggingfacehub["repo_id"],
                task=config.huggingfacehub["task"],
                huggingfacehub_api_token=config.huggingfacehub[
                    "huggingfacehub_api_token"
                ],
            )
        else:  # sagemaker by default
            content_handler = ContentHandler()
            self.embeddings = SagemakerEndpointEmbeddings(
                endpoint_name=config.sagemaker["endpoint_name"],
                region_name=config.sagemaker["region_name"],
                content_handler=content_handler,
            )

        self.api = FastAPI()
        self.vectorstore = ElasticVectorSearch(
            elasticsearch_url=config.es_url,
            index_name=config.product_index_name,
            embedding=self.embeddings,
        )
        self.elasticStore = ElasticsearchVectorStoreIndex(self.vectorstore)
        self.products_indexer = ProductsIndexer(self.elasticStore)
        self.products_handler = ProductsHandler(self.products_indexer)
        self.api.include_router(self.products_handler.router)

        content_base_content_handler = ContentHandler()
        self.content_base_embeddings = SagemakerEndpointEmbeddingsKeys(
                aws_key=config.sagemaker_aws["aws_key"],
                aws_secret=config.sagemaker_aws["aws_secret"],
                endpoint_name=config.sagemaker_aws["endpoint_name"],
                region_name=config.sagemaker_aws["region_name"],
                content_handler=content_base_content_handler,
            )
        self.content_base_vectorstore = ElasticVectorSearch(
            elasticsearch_url=config.es_url,
            index_name=config.content_base_index_name,
            embedding=self.content_base_embeddings,
        )
        self.custom_elasticStore = ContentBaseElasticsearchVectorStoreIndex(self.content_base_vectorstore)
        self.content_base_indexer = ContentBaseIndexer(self.custom_elasticStore)
        self.content_base_handler = ContentBaseHandler(self.content_base_indexer)
        self.api.include_router(self.content_base_handler.router)

config = AppConfig()
main_app = App(config)
