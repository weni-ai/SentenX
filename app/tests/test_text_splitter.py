import unittest
from app.text_splitters.text_splitters import (
    TextSplitter, character_text_splitter
)
from lorem_text import lorem


class TestProductsHandler(unittest.TestCase):
    def setUp(self):
        self.text = lorem.paragraphs(5)

    def test_character_text_splitter(self):
        splitter = TextSplitter(character_text_splitter, self.text)
        chunks = splitter.split_text()
        self.assertEqual(type(chunks), list)
        self.assertGreaterEqual(len(chunks), len(chunks))
