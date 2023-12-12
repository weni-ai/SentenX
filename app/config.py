import os
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    def __init__(self):
        self.product_index_name = os.environ.get(
            "INDEX_PRODUCTS_NAME", "catalog_products"
        )
        self.es_url = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
        self.embedding_type = os.environ.get("EMBEDDING_TYPE", "sagemaker")
        self.sagemaker = {
            "endpoint_name": os.environ.get(
                "SAGEMAKER_ENDPOINT_NAME",
                "huggingface-pytorch-inference-2023-07-28-21-01-20-147",
            ),
            "region_name": os.environ.get("SAGEMAKER_REGION_NAME", "us-east-1"),
        }
        self.huggingfacehub = {
            "repo_id": os.environ.get(
                "HUGGINGFACE_REPO_ID", "sentence-transformers/all-MiniLM-L6-v2"
            ),
            "task": os.environ.get("HUGGINGFACE_TASK", "feature-extraction"),
            "huggingfacehub_api_token": os.environ.get(
                "HUGGINGFACE_API_TOKEN", "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"
            ),
        }

        self.sagemaker_aws ={
            "endpoint_name": os.environ.get(
                "SAGEMAKER_ENDPOINT_NAME",
                "huggingface-pytorch-inference-2023-10-25-14-25-59-713",
            ),
            "region_name": os.environ.get("SAGEMAKER_REGION_NAME", "us-east-1"),
            "aws_key": os.environ.get("SAGE_MAKER_AWS_KEY"),
            "aws_secret": os.environ.get("SAGE_MAKER_AWS_SECRET"),
        }

        self.content_base_index_name = os.environ.get(
            "INDEX_PRODUCTS_NAME", "content_bases"
        )
