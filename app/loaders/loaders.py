from langchain.document_loaders import (
    TextLoader, PyPDFLoader, UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader, Docx2txtLoader
)
from typing import Callable, List
from langchain.schema.document import Document


class DataLoader:
    def __init__(self, loader: Callable, file: str) -> None:
        self.loader = loader
        self.file = file

    def load(self) -> List[Document]:
        return self.loader(self.file)

    def raw_text(self) -> str:
        pages = self.load()
        raw_text = ""
        for i, page in enumerate(pages):
            text = page.page_content
            if text:
                raw_text += text.lower()
        return raw_text


def txt_loader(file: str) -> Callable:
    loader = TextLoader(file)
    return loader.load()


def pdf_loader(file: str) -> Callable:
    loader = PyPDFLoader(file)
    pages = loader.load_and_split()
    return pages


def docx_loader(file: str) -> Callable:
    loader = Docx2txtLoader(file)
    return loader.load()


def u_docx_loader(file: str) -> Callable:
    """Same as docx_loader but using Unstructured"""
    loader = UnstructuredWordDocumentLoader(file)
    return loader.load()


def xlsx_loader(file: str) -> Callable:
    """Loads .xlsx and .xls files"""
    loader = UnstructuredExcelLoader(file, mode="elements")
    return loader.load()
