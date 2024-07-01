from app.loaders import (
    load_file_and_get_raw_text,
    load_file_url_and_get_raw_text,
    load_file_url_and_split_text
)
from app.text_splitters import get_split_text
from typing import Dict, List
from fastapi.logger import logger
from langchain.schema.document import Document
from app.indexer import IDocumentIndexer
from app.downloaders import IFileDownloader
from app.text_splitters import ITextSplitter


def get_file_metadata(content_base: Dict) -> Dict[str, str]:
    return {
        'source': content_base.get("filename"),
        "content_base_uuid": str(content_base.get('content_base'))
    }


def add_file_metadata(
    document_pages: List[Document],
    content_base: Dict
) -> List[Document]:
    metadata = {
        "content_base_uuid": str(content_base.get('content_base')),
        "filename": content_base.get("filename"),
        "file_uuid": content_base.get("file_uuid")

    }
    for page in document_pages:
        page.metadata.update(metadata)

    return document_pages


class IndexerFileManager:

    """Business rule to index a file"""

    def __init__(self,
                 file_downloader: IFileDownloader,
                 content_base_indexer: IDocumentIndexer,
                 text_splitter: ITextSplitter,
                 ) -> None:
        self.file_downloader = file_downloader
        self.content_base_indexer = content_base_indexer
        self.text_splitter = text_splitter

    def index_file_url(self, content_base, **kwargs) -> bool:
        load_type = content_base.get("load_type")

        docs: List[Document]
        full_content: str

        docs, full_content  = load_file_url_and_split_text(
            content_base.get("file"),
            content_base.get('extension_file'),
            self.text_splitter,
            load_type=load_type
        )
        document_pages: List[Document] = add_file_metadata(docs, content_base)
        try:
            self.content_base_indexer.index_documents(document_pages)
            self.content_base_indexer.index_doc_content(
                full_content=full_content,
                content_base_uuid=str(content_base.get('content_base')),
                filename=content_base.get("filename"),
                file_uuid=content_base.get("file_uuid"),
            )
            return True
        except Exception as e:  # TODO: handle exceptions
            logger.exception(e)
            return False

    def index_file_url_raw_text(self, content_base):
        file_raw_text: str = load_file_url_and_get_raw_text(
            content_base.get("file"), content_base.get('extension_file')
        )
        metadatas: Dict[str, str] = get_file_metadata(content_base)
        texts: List[str] = get_split_text(file_raw_text)

        try:
            self.content_base_indexer.index(texts, metadatas)
            return True
        except Exception as e:  # TODO: handle exceptions
            logger.exception(e)
            return False

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
