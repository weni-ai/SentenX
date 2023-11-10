from typing import Callable, List
from langchain.text_splitter import CharacterTextSplitter
from app.util import count_words
import os

DEFAULT_CHUNK_SIZE = os.environ.get("DEFAULT_CHUNK_SIZE", 75)
DEFAULT_CHUNK_OVERLAP = os.environ.get("DEFAULT_CHUNK_OVERLAP", 75)
DEFAULT_SEPARATOR = os.environ.get("DEFAULT_SEPARATOR", "\n")


class TextSplitter:
    def __init__(self, splitter: Callable, content: str) -> None:
        self.splitter = splitter
        self.content = content

    def split_text(self) -> Callable:
        return self.splitter(self.content)


def character_text_splitter(
        content: str,
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
    pages = text_splitter.split_text(content)
    return pages
