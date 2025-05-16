from tests import unittest

from jmespath import lexer
from jmespath.exceptions import LexerError, EmptyExpressionError

class LexerUtils(unittest.TestCase):

    def assert_tokens(self, actual, expected):
        # The expected tokens only need to specify the
        # type and value.  The line/column numbers are not
        # checked, and we use assertEqual for the tests
        # that check those line numbers.
        stripped = []
        for item in actual:
            stripped.append({'type': item['type'], 'value': item['value']})
        # Every tokenization should end in eof, so we automatically
        # check that value, strip it off the end, and then
        # verify the remaining tokens against the expected.
        # That way the tests don't need to add eof to every
        # assert_tokens call.
        self.assertEqual(stripped[-1]['type'], 'eof')
        stripped.pop()
        self.assertEqual(stripped, expected)

class TestRegexLexer(LexerUtils):

    def setUp(self):
        self.lexer = lexer.Lexer()

    def test_empty_string(self):
        with self.assertRaises(EmptyExpressionError):
            list(self.lexer.tokenize(''))

    def test_field(self):
        tokens = list(self.lexer.tokenize('foo'))
        self.assert_tokens(tokens, [{'type': 'unquoted_identifier',
                                     'value': 'foo'}])

    def test_number(self):
        tokens = list(self.lexer.tokenize('24'))
        self.assert_tokens(tokens, [{'type': 'number',
                                     'value': 24}])

    def test_negative_number(self):
        tokens = list(self.lexer.tokenize('-24'))
        self.assert_tokens(tokens, [{'type': 'number',
                                     'value': -24}])

    def test_plus(self):
        tokens = list(self.lexer.tokenize('+'))
        self.assert_tokens(tokens, [{'type': 'plus',
                                     'value': '+'}])

    def test_minus(self):
        tokens = list(self.lexer.tokenize('-'))
        self.assert_tokens(tokens, [{'type': 'minus',
                                     'value': '-'}])
    def test_minus_unicode(self):
        tokens = list(self.lexer.tokenize(u'\u2212'))
        self.assert_tokens(tokens, [{'type': 'minus',
                                     'value': u'\u2212'}])

    def test_multiplication(self):
        tokens = list(self.lexer.tokenize('*'))
        self.assert_tokens(tokens, [{'type': 'star',
                                     'value': '*'}])

    def test_multiplication_unicode(self):
        tokens = list(self.lexer.tokenize(u'\u00d7'))
        self.assert_tokens(tokens, [{'type': 'multiply',
                                     'value': u'\u00d7'}])

    def test_division(self):
        tokens = list(self.lexer.tokenize('/'))
        self.assert_tokens(tokens, [{'type': 'divide',
                                     'value': '/'}])

    def test_division_unicode(self):
        tokens = list(self.lexer.tokenize('÷'))
        self.assert_tokens(tokens, [{'type': 'divide',
                                     'value': '÷'}])

    def test_modulo(self):
        tokens = list(self.lexer.tokenize('%'))
        self.assert_tokens(tokens, [{'type': 'modulo',
                                     'value': '%'}])

    def test_integer_division(self):
        tokens = list(self.lexer.tokenize('//'))
        self.assert_tokens(tokens, [{'type': 'div',
                                     'value': '//'}])

    def test_quoted_identifier(self):
        tokens = list(self.lexer.tokenize('"foobar"'))
        self.assert_tokens(tokens, [{'type': 'quoted_identifier',
                                     'value': "foobar"}])

    def test_json_escaped_value(self):
        tokens = list(self.lexer.tokenize('"\u2713"'))
        self.assert_tokens(tokens, [{'type': 'quoted_identifier',
                                     'value': u"\u2713"}])

    def test_number_expressions(self):
        tokens = list(self.lexer.tokenize('foo.bar.baz'))
        self.assert_tokens(tokens, [
            {'type': 'unquoted_identifier', 'value': 'foo'},
            {'type': 'dot', 'value': '.'},
            {'type': 'unquoted_identifier', 'value': 'bar'},
            {'type': 'dot', 'value': '.'},
            {'type': 'unquoted_identifier', 'value': 'baz'},
        ])

    def test_space_separated(self):
        tokens = list(self.lexer.tokenize('foo.bar[*].baz | a || b'))
        self.assert_tokens(tokens, [
            {'type': 'unquoted_identifier', 'value': 'foo'},
            {'type': 'dot', 'value': '.'},
            {'type': 'unquoted_identifier', 'value': 'bar'},
            {'type': 'lbracket', 'value': '['},
            {'type': 'star', 'value': '*'},
            {'type': 'rbracket', 'value': ']'},
            {'type': 'dot', 'value': '.'},
            {'type': 'unquoted_identifier', 'value': 'baz'},
            {'type': 'pipe', 'value': '|'},
            {'type': 'unquoted_identifier', 'value': 'a'},
            {'type': 'or', 'value': '||'},
            {'type': 'unquoted_identifier', 'value': 'b'},
        ])

    def test_literal(self):
        tokens = list(self.lexer.tokenize('`[0, 1]`'))
        self.assert_tokens(tokens, [
            {'type': 'literal', 'value': [0, 1]},
        ])

    def test_literal_string(self):
        tokens = list(self.lexer.tokenize('`"foobar"`'))
        self.assert_tokens(tokens, [
            {'type': 'literal', 'value': "foobar"},
        ])

    def test_literal_number(self):
        tokens = list(self.lexer.tokenize('`2`'))
        self.assert_tokens(tokens, [
            {'type': 'literal', 'value': 2},
        ])

    def test_raw_string_literal(self):
        tokens = list(self.lexer.tokenize("'foo'"))
        self.assert_tokens(tokens, [
            {'type': 'literal', 'value': 'foo'}
        ])

    def test_raw_string_literal_preserve_escape(self):
        tokens = list(self.lexer.tokenize("'foo\\z'"))
        self.assert_tokens(tokens, [
            {'type': 'literal', 'value': 'foo\\z'}
        ])

    def test_raw_string_literal_escaped_apostrophe(self):
        tokens = list(self.lexer.tokenize("'foo\\\'bar'"))
        self.assert_tokens(tokens, [
            {'type': 'literal', 'value': 'foo\'bar'}
        ])

    def test_raw_string_literal_escaped_reverse_solidus(self):
        tokens = list(self.lexer.tokenize("'foo\\\\bar'"))
        self.assert_tokens(tokens, [
            {'type': 'literal', 'value': 'foo\\bar'}
        ])

    def test_position_information(self):
        tokens = list(self.lexer.tokenize('foo'))
        self.assertEqual(
            tokens,
            [{'type': 'unquoted_identifier', 'value': 'foo',
              'start': 0, 'end': 3},
              {'type': 'eof', 'value': '', 'start': 3, 'end': 3}]
        )

    def test_position_multiple_tokens(self):
        tokens = list(self.lexer.tokenize('foo.bar'))
        self.assertEqual(
            tokens,
            [{'type': 'unquoted_identifier', 'value': 'foo',
              'start': 0, 'end': 3},
             {'type': 'dot', 'value': '.',
              'start': 3, 'end': 4},
             {'type': 'unquoted_identifier', 'value': 'bar',
              'start': 4, 'end': 7},
             {'type': 'eof', 'value': '',
              'start': 7, 'end': 7},
             ]
        )

    def test_root_reference(self):
        tokens = list(self.lexer.tokenize('$[0]'))
        self.assertEqual(
            tokens,
            [{'type': 'root', 'value': '$',
                'start': 0, 'end': 1},
            {'type': 'lbracket', 'value':
                '[', 'start': 1, 'end': 2},
            {'type': 'number', 'value': 0,
                'start': 2, 'end': 3},
            {'type': 'rbracket', 'value': ']',
                'start': 3, 'end': 4},
            {'type': 'eof', 'value': '',
                'start': 4, 'end': 4}
            ]
        )

    def test_variable(self):
        tokens = list(self.lexer.tokenize('$foo'))
        self.assertEqual(
            tokens,
            [{'type': 'variable', 'value': '$foo',
              'start': 0, 'end': 4},
            {'type': 'eof', 'value': '',
                'start': 4, 'end': 4}
              ]
        )

    def test_ternary(self):
        tokens = list(self.lexer.tokenize('true ? false : foo'))
        self.assertEqual(
            tokens,
            [
                { 'type': 'unquoted_identifier', 'value': 'true', 'start': 0, 'end': 4 },
                { 'type': 'question', 'value': '?', 'start': 5, 'end': 6 },
                { 'type': 'unquoted_identifier', 'value': 'false', 'start': 7, 'end': 12 },
                { 'type': 'colon', 'value': ':', 'start': 13, 'end': 14 },
                { 'type': 'unquoted_identifier', 'value': 'foo', 'start': 15, 'end': 18 },
                { 'type': 'eof', 'value': '', 'start': 18, 'end': 18 }
            ]
        )

    def test_unknown_character(self):
        with self.assertRaises(LexerError) as e:
            tokens = list(self.lexer.tokenize('foo[0^]'))

    def test_bad_first_character(self):
        with self.assertRaises(LexerError):
            tokens = list(self.lexer.tokenize('^foo[0]'))

    def test_arithmetic_expression(self):
        tokens = list(self.lexer.tokenize('foo-bar'))
        self.assertEqual(
            tokens,
            [
                {'type': 'unquoted_identifier', 'value': 'foo', 'start': 0, 'end': 3},
                {'type': 'minus', 'value': '-', 'start': 3, 'end': 4},
                {'type': 'unquoted_identifier', 'value': 'bar', 'start': 4, 'end': 7},
                {'type': 'eof', 'value': '', 'start': 7, 'end': 7}
            ]
        )

    def test_invalid_character_in_json_literal(self):
        with self.assertRaises(LexerError) as e:
            tokens = list(self.lexer.tokenize(u'`0\u2028`'))

if __name__ == '__main__':
    unittest.main()
