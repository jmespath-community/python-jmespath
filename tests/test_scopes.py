
import pytest

from tests import unittest
from jmespath.visitor import Scope

class TestScope(unittest.TestCase):
    def setUp(self):
        None

    def test_Scope_missing(self):
        scope = Scope(None)
        value = scope.getValue('foo')
        self.assertEqual(None, value)

    def test_Scope_root(self):
        scope = Scope({'foo': 'bar'})
        value = scope.getValue('foo')
        self.assertEqual('bar', value)

    def test_Scope_nested(self):

        def nested(scope):

            def inner(scope):
                value = scope.getValue('foo')
                self.assertEqual('baz', value)
                value = scope.getValue('qux')
                self.assertEqual('quux', value)

            inner(scope.withScope({'foo': 'baz'}))

            value = scope.getValue('foo')
            self.assertEqual('bar', value)

            value = scope.getValue('qux')
            self.assertEqual('quux', value)

        scope = Scope(None)

        nested(scope.withScope({'foo': 'bar', 'qux': 'quux'}))

        value = scope.getValue('foo')
        self.assertEqual(None, value)

if __name__ == '__main__':
	unittest.main()