
import os
from app.loaders.loaders import (
    DataLoader,
    txt_loader,
    pdf_loader,
    docx_loader,
    xlsx_loader,
)
from app.loaders.loaders import (
    DataLoaderCls,
    PDFLoader,
    DocxLoader,
    TxtLoader,
    XlsxLoader,
    URLsLoader,
)
from langchain.schema.document import Document
from typing import List
from app.text_splitters import ITextSplitter

supported_loaders = {
    'txt': txt_loader,
    'pdf': pdf_loader,
    'doc': docx_loader,
    'docx': docx_loader,
    'xls': xlsx_loader,
    'xlsx': xlsx_loader,
}

supported_loaders_cls = {
    'pdf': PDFLoader,
    'doc': DocxLoader,
    'docx': DocxLoader,
    'txt': TxtLoader,
    'xlsx': XlsxLoader,
    'xls': XlsxLoader,
    'urls': URLsLoader,
}

def load_file_and_get_raw_text(file_name: str, file_type: str) -> str:
    file_path = f'{os.environ.get("FILE_PATH")}/{file_name}'
    loader = supported_loaders.get(file_type)
    data_loader = DataLoader(loader, file_path)
    return data_loader.raw_text()


def load_file_url_and_get_raw_text(file_url: str, file_type: str) -> str:
    loader = supported_loaders.get(file_type)
    data_loader = DataLoader(loader, file_url)
    return data_loader.raw_text()


def load_file_url_and_get_pages_text(file_url: str, file_type: str) -> List[Document]:
    loader = supported_loaders.get(file_type)
    data_loader = DataLoader(loader, file_url)
    return data_loader.load()


def load_file_url_and_split_text(file_url: str, file_type: str, text_splitter: ITextSplitter) -> List[Document]:
    loader = supported_loaders_cls.get(file_type)
    data_loader = DataLoaderCls(loader, file_url)
    return data_loader.load_and_split_text(text_splitter)
