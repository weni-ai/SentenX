import os
import boto3
from app.downloaders import IFileDownloader
from fastapi.logger import logger
from urllib.parse import urlparse
from typing import Tuple, List


class S3FileDownloader(IFileDownloader):

    def __init__(self, 
                 access_key: str,
                 secret_key: str,
                 bucket_name: str = os.environ.get("AWS_STORAGE_BUCKET_NAME"),
        ) -> None:
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.client = self.authenticate()

    def authenticate(self):
        return boto3.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )

    def download_file(self, file_name):
        bucket = self.bucket_name
        key = file_name
        local_path = f"app/files/{file_name}"

        self.client.download_file(bucket, key, local_path)

    def download_file_batch(self):
        raise NotImplementedError

    def download_file_bulk(self):
        raise NotImplementedError


def get_s3_bucket_and_file_name(file_url: str)-> Tuple[str, ...]:
    result = urlparse(file_url)
    bucket_name = result.netloc.split('.s3')[0]
    file_name = result.path.strip('/')
    return bucket_name, file_name
