from tests.legacy import unittest
from tests import test_lexer

from jmespath import lexer
from jmespath.visitor import Options
from jmespath.exceptions import LexerError


class TestLegacyRegexLexer(test_lexer.LexerUtils):

    def setUp(self):
        self.lexer = lexer.Lexer()
        self.options = Options(enable_legacy_literals=True)

    def tokenize(self, expression):
        return self.lexer.tokenize(expression, self.options)

    def test_literal_string(self):
        tokens = list(self.tokenize('`foobar`'))
        self.assert_tokens(tokens, [
            {'type': 'literal', 'value': "foobar"},
        ])

    def test_literal_with_invalid_json(self):
        with self.assertRaises(LexerError):
            list(self.tokenize('`foo"bar`'))

    def test_literal_with_empty_string(self):
        tokens = list(self.tokenize('``'))
        self.assert_tokens(tokens, [{'type': 'literal', 'value': ''}])

    def test_adds_quotes_when_invalid_json(self):
        tokens = list(self.tokenize('`{{}`'))
        self.assertEqual(
            tokens,
            [{'type': 'literal', 'value': '{{}',
              'start': 0, 'end': 4},
             {'type': 'eof', 'value': '',
              'start': 5, 'end': 5}
             ]
        )

if __name__ == '__main__':
    unittest.main()
