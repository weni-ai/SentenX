from app.loaders.loaders import (DataLoader, txt_loader, pdf_loader, docx_loader, xlsx_loader)


supported_loaders = {
    'txt': txt_loader,
    'pdf': pdf_loader,
    'doc': docx_loader,
    'docx': docx_loader,
    'xls': xlsx_loader,
    'xlsx': xlsx_loader,
}


def load_file_and_get_raw_text(file_name: str, file_type: str):
    file_path = f'app/files/{file_name}'
    loader = supported_loaders.get(file_type)
    data_loader = DataLoader(loader, file_path)
    return data_loader.raw_text()