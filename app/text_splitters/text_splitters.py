from typing import Callable, List
from langchain.text_splitter import CharacterTextSplitter
from app.util import count_words
import os

DEFAULT_CHUNK_SIZE = os.environ.get("DEFAULT_CHUNK_SIZE", 75)
DEFAULT_CHUNK_OVERLAP = os.environ.get("DEFAULT_CHUNK_OVERLAP", 75)
DEFAULT_SEPARATOR = os.environ.get("DEFAULT_SEPARATOR", "\n")


class TextSplitter:
    def __init__(self, text_splitter: Callable, content: str) -> None:
        self.text_splitter = text_splitter
        self.content = content

    def split_text(self) -> Callable:
        pages = self.text_splitter.split_text(self.content)
        return pages
    
    def create_documents(self, metadatas: dict):
        return self.text_splitter.create_documents(self.content, metadatas=metadatas)


def character_text_splitter(
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        length_function: Callable = count_words,
        separator: str = DEFAULT_SEPARATOR) -> List:

    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=length_function,
        separator=separator,
    )
    return text_splitter


def get_split_text(raw_data: str):
    text_splitter = TextSplitter(character_text_splitter(), raw_data)
    texts = text_splitter.split_text()
    return texts