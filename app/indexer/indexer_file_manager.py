from app.loaders import load_file_and_get_raw_text
from app.text_splitters import get_split_text
from typing import Dict, List
from fastapi.logger import logger


def get_file_metadata(content_base: Dict) -> Dict[str, str]:
    return {
            'source': content_base.get("filename"),
            "content_base_uuid": str(content_base.get('content_base'))
        }


class IndexerFileManager:

    """Business rule to index a file"""

    def __init__(self, file_downloader, content_base_indexer) -> None:
        self.file_downloader = file_downloader
        self.content_base_indexer = content_base_indexer
    
    def index_file(self, content_base):
        filename: str = content_base.get("filename")

        try:
            self.file_downloader.download_file(filename)
        except Exception as err:
            logger.exception(err)
            return False

        file_raw_text: str = load_file_and_get_raw_text(
                filename, content_base.get('extension_file')
            )
        metadatas: Dict[str, str] = get_file_metadata(content_base)
        texts: List[str] = get_split_text(file_raw_text)

        try:
            self.content_base_indexer.index(texts, metadatas)
            return True
        except Exception as e:  # TODO: handle exceptions
            logger.exception(e)
            return False
