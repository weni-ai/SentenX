import unittest
from app.loaders.loaders import (
    DataLoader,
    pdf_loader,
    txt_loader,
    docx_loader,
    u_docx_loader,
    xlsx_loader
)
import os
import pathlib
import shutil
import xlsxwriter
from docx import Document
from reportlab.pdfgen.canvas import Canvas


class TestDocumentLoader(unittest.TestCase):
    test_dir = pathlib.Path(__file__).parent.resolve()
    path = os.path.join(test_dir, 'test_files')
    text_string = 'Hello, World!'
    file_name = 'test_file'

    @staticmethod
    def _create_test_dir():
        if not os.path.exists(TestDocumentLoader.path):
            os.mkdir(TestDocumentLoader.path)

    @staticmethod
    def _create_pdf(path: str, name: str, text: str):
        file_path = f'{path}/{name}.pdf'
        canvas = Canvas(file_path)
        canvas.drawString(72, 72, text)
        canvas.save()

    @staticmethod
    def _create_txt(path: str, name: str, text: str):
        file_path = f'{path}/{name}.txt'
        with open(file_path, 'w') as f:
            f.write(text)

    @staticmethod
    def _create_docx(path: str, name: str, text: str):
        file_path = f'{path}/{name}.docx'
        document = Document()
        document.add_paragraph(text, style='Intense Quote')
        document.save(file_path)

    @staticmethod
    def _create_xlsx(path: str, name: str):
        file_path = f'{path}/{name}.xlsx'
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet("Test sheet")
        scores = (
            ['Lorem', 4576],
            ['Ipsum',   345],
            ['Dolor',  9088],
            ['Sit',    88],
            ['Amet',    15],
        )
        row = 0
        col = 0
        for name, score in (scores):
            worksheet.write(row, col, name)
            worksheet.write(row, col + 1, score)
            row += 1
        workbook.close()

    @classmethod
    def setUpClass(cls) -> None:
        cls._create_test_dir()
        cls._create_pdf(cls.path, cls.file_name, cls.text_string)
        cls._create_txt(cls.path, cls.file_name, cls.text_string)
        cls._create_docx(cls.path, cls.file_name, cls.text_string)
        cls._create_xlsx(cls.path, cls.file_name)

    def test_load_pdf(self):
        file_path = f'{self.path}/{self.file_name}.pdf'
        data_loader = DataLoader(pdf_loader, file_path)
        raw_text = data_loader.raw_text()
        self.assertEqual(raw_text, self.text_string.lower())

    def test_load_txt(self):
        file_path = f'{self.path}/{self.file_name}.txt'
        data_loader = DataLoader(txt_loader, file_path)
        raw_text = data_loader.raw_text()
        self.assertEqual(raw_text, self.text_string.lower())

    def test_load_udocx(self):
        file_path = f'{self.path}/{self.file_name}.docx'
        data_loader = DataLoader(u_docx_loader, file_path)
        raw_text = data_loader.raw_text()
        self.assertEqual(raw_text, self.text_string.lower())

    def test_load_docx(self):
        file_path = f'{self.path}/{self.file_name}.docx'
        data_loader = DataLoader(docx_loader, file_path)
        raw_text = data_loader.raw_text()
        self.assertEqual(raw_text, self.text_string.lower())

    def test_load_xlsx(self):
        file_path = f'{self.path}/{self.file_name}.xlsx'
        data_loader = DataLoader(xlsx_loader, file_path)
        raw_text = data_loader.raw_text()
        self.assertEqual(type(raw_text), str)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TestDocumentLoader.path):
            shutil.rmtree(TestDocumentLoader.path, ignore_errors=True)
