import os
from celery import Celery

from typing import Dict
from app.indexer.indexer_file_manager import IndexerFileManager
from app.downloaders.s3 import S3FileDownloader

from app.handlers.content_bases import NexusRESTClient

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
        "CELERY_BROKER_URL", "redis://localhost:6379"
    )
celery.conf.result_backend = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379"
    )


@celery.task(name="index_file")
def index_file_data(content_base: Dict) -> bool:
    from app.main import main_app

    file_downloader = S3FileDownloader(
        os.environ.get("AWS_STORAGE_ACCESS_KEY"),
        os.environ.get("AWS_STORAGE_SECRET_KEY")
    )
    manager = IndexerFileManager(file_downloader, main_app.content_base_indexer)
    index_result: bool = manager.index_file(content_base)
    NexusRESTClient().index_succedded(task_succeded=index_result, nexus_task_uuid=content_base.get("task_uuid"))

    return manager.index_file(content_base)
