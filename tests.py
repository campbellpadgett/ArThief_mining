
























import unittest
from utils import isNotLatinAlphabet


class TestIsNotLatinAlphabet(unittest.TestCase):

    def setUp(self) -> None:
        self.false_terms = ['hello', '123456', '*&^gzdl3ts', 'Salve']
        self.true_terms = ['你好', 'привет', 'नमस्ते']

    def test_isNotLatinAlphabet_false(self):
        for term in self.false_terms:
            self.assertFalse(isNotLatinAlphabet(term))

    def test_isNotLatinAlphabet_true(self):
        for term in self.true_terms:
            self.assertTrue(isNotLatinAlphabet(term))

    def tearDown(self) -> None:
        del self.false_terms, self.true_terms


if __name__ == '__main__':
    unittest.main()
