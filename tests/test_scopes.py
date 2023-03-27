
import pytest

from tests import unittest
from jmespath.visitor import Scopes

class TestScope(unittest.TestCase):
    def setUp(self):
        self._scopes = Scopes('root')

    def test_Scope_missing(self):
        value = self._scopes.getValue('foo')
        self.assertEqual(None, value)

    def test_Scope_root(self):
        value = self._scopes.getRoot()
        self.assertEqual('root', value)

    def test_Scope_nested(self):
        self._scopes.pushScope({'foo': 'bar'})
        self._scopes.pushScope({'foo': 'baz'})
        value = self._scopes.getValue('foo')
        self.assertEqual('baz', value)

if __name__ == '__main__':
	unittest.main()