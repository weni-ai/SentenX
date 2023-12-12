from abc import ABC, abstractmethod
from app.downloaders.exceptions import FileDownloaderException


class IFileDownloader(ABC):
    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def download_file(self):
        pass

    @abstractmethod
    def download_file_batch(self):
        pass

    @abstractmethod
    def download_file_bulk(self):
        pass

def download_file(file_downloader, file_name: str) -> None:
    handler = file_downloader
    try:
        handler.download_file(file_name)
    except Exception as err:
        raise FileDownloaderException(err)