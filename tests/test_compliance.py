import os
from pprint import pformat
from tests import OrderedDict
from tests import json

import pytest

from jmespath.visitor import Options


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
COMPLIANCE_DIR = os.path.join(TEST_DIR, 'compliance')
LEGACY_DIR = os.path.join(TEST_DIR, 'legacy')
NOT_SPECIFIED = object()
COMPLIANCE_OPTIONS = Options(dict_cls=OrderedDict)
LEGACY_OPTIONS = Options(dict_cls=OrderedDict, enable_legacy_literals=True)


def _compliance_tests(requested_test_type):
    for full_path in _walk_files():
        if full_path.endswith('.json'):
            for given, test_type, test_data in load_cases(full_path):
                t = test_data
                # Benchmark tests aren't run as part of the normal
                # test suite, so we only care about 'result' and
                # 'error' test_types.
                if test_type == 'result' and test_type == requested_test_type:
                    yield (given, t['expression'],
                           t['result'], os.path.basename(full_path))
                elif test_type == 'error' and test_type == requested_test_type:
                    yield (given, t['expression'],
                           t['error'], os.path.basename(full_path))


def _walk_files():
    # Check for a shortcut when running the tests interactively.
    # If a JMESPATH_TEST is defined, that file is used as the
    # only test to run.  Useful when doing feature development.
    single_file = os.environ.get('JMESPATH_TEST')
    if single_file is not None:
        yield os.path.abspath(single_file)
    else:
        for root, dirnames, filenames in os.walk(TEST_DIR):
            for filename in filenames:
                yield os.path.join(root, filename)
        for root, dirnames, filenames in os.walk(LEGACY_DIR):
            for filename in filenames:
                yield os.path.join(root, filename)


def load_cases(full_path):
    all_test_data = json.load(open(full_path), object_pairs_hook=OrderedDict)
    for test_data in all_test_data:
        given = test_data['given']
        for case in test_data['cases']:
            if 'result' in case:
                test_type = 'result'
            elif 'error' in case:
                test_type = 'error'
            elif 'bench' in case:
                test_type = 'bench'
            else:
                raise RuntimeError("Unknown test type: %s" % json.dumps(case))
            yield (given, test_type, case)


@pytest.mark.parametrize(
    'given, expression, expected, filename',
    _compliance_tests('result')
)
def test_expression(given, expression, expected, filename):
    try:
        (actual, parsed) = _search_expression(given, expression, filename)
    except ValueError as e:
        raise AssertionError(
            'jmespath expression failed to compile: "%s", error: %s"' %
            (expression, e))

    expected_repr = json.dumps(expected, indent=4)
    actual_repr = json.dumps(actual, indent=4)
    error_msg = ("\n\n  (%s) The expression '%s' was supposed to give:\n%s\n"
                 "Instead it matched:\n%s\nparsed as:\n%s\ngiven:\n%s" % (
                     filename, expression, expected_repr,
                     actual_repr, pformat(parsed.parsed),
                     json.dumps(given, indent=4)))
    error_msg = error_msg.replace(r'\n', '\n')
    assert actual == expected, error_msg


@pytest.mark.parametrize(
    'given, expression, error, filename',
    _compliance_tests('error')
)
def test_error_expression(given, expression, error, filename):
    if error not in ('syntax', 'invalid-type',
                     'unknown-function', 'invalid-arity', 'invalid-value'):
        raise RuntimeError("Unknown error type '%s'" % error)
    try:
        (_, parsed) = _search_expression(given, expression, filename)
    except ValueError:
        # Test passes, it raised a parse error as expected.
        pass
    except Exception as e:
        # Failure because an unexpected exception was raised.
        error_msg = ("\n\n  (%s) The expression '%s' was suppose to be a "
                     "syntax error, but it raised an unexpected error:\n\n%s" % (
                         filename, expression, e))
        error_msg = error_msg.replace(r'\n', '\n')
        raise AssertionError(error_msg)
    else:
        error_msg = ("\n\n  (%s) The expression '%s' was suppose to be a "
                     "syntax error, but it successfully parsed as:\n\n%s" % (
                         filename, expression, pformat(parsed.parsed)))
        error_msg = error_msg.replace(r'\n', '\n')
        raise AssertionError(error_msg)

def _search_expression(given, expression, filename):
    import jmespath.parser

    options = LEGACY_OPTIONS \
        if filename.startswith('legacy') \
        else COMPLIANCE_OPTIONS

    ## This test suite contains identical expressions
    ## tested against both a legacy and a JEP-12
    ## standards-compliant parser.

    ## However, the Parser() class contains a cache
    ## of compiled expressions for performance purposes

    ## To prevent conflicts between legacy and JEP-12
    ## standards-compliant evaluation, we need to
    ## clear the cache here

    jmespath.parser.Parser()._free_cache_entries()

    parsed = jmespath.compile(expression, options=options)
    actual = parsed.search(given, options=options)
    return (actual, parsed)