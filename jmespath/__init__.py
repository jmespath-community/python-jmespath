from jmespath import parser
from jmespath.visitor import Options

__version__ = '1.1.0'


def compile(expression, options=None):
    return parser.Parser().parse(expression, options=options)


def search(expression, data, options=None):
    return compile(expression, options).search(data, options=options)
