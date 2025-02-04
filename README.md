# JMESPath Community

[![image](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jmespath/chat)

JMESPath (pronounced "james path") allows you to declaratively specify
how to extract elements from a JSON document.

JMESPath Community is an unofficial community effort to promote
improvements and updates to the JMESPath language specification.

For example, given this document:

    {"foo": {"bar": "baz"}}

The jmespath expression `foo.bar` will return "baz".

JMESPath also supports:

Referencing elements in a list. Given the data:

    {"foo": {"bar": ["one", "two"]}}

The expression: `foo.bar[0]` will return "one". You can also reference
all the items in a list using the `*` syntax:

    {"foo": {"bar": [{"name": "one"}, {"name": "two"}]}}

The expression: `foo.bar[*].name` will return \["one", "two"\]. Negative
indexing is also supported (-1 refers to the last element in the list).
Given the data above, the expression `foo.bar[-1].name` will return
"two".

The `*` can also be used for hash types:

    {"foo": {"bar": {"name": "one"}, "baz": {"name": "two"}}}

The expression: `foo.*.name` will return \["one", "two"\].

# Installation

You can install JMESPath Community from PyPI with:

``` bash
pip install jmespath-community
```

# API

The `jmespath.py` library has two functions that operate on python data
structures. You can use `search` and give it the jmespath expression and
the data:

``` python
>>> import jmespath
>>> path = jmespath.search('foo.bar', {'foo': {'bar': 'baz'}})
'baz'
```

Similar to the `re` module, you can use the `compile` function to
compile the JMESPath expression and use this parsed expression to
perform repeated searches:

``` python
>>> import jmespath
>>> expression = jmespath.compile('foo.bar')
>>> expression.search({'foo': {'bar': 'baz'}})
'baz'
>>> expression.search({'foo': {'bar': 'other'}})
'other'
```

This is useful if you're going to use the same jmespath expression to
search multiple documents. This avoids having to reparse the JMESPath
expression each time you search a new document.

## Options

You can provide an instance of `jmespath.Options` to control how a
JMESPath expression is evaluated. The most common scenario for using an
`Options` instance is if you want to have ordered output of your dict
keys. To do this you can use either of these options:

``` python
>>> import jmespath
>>> jmespath.search('{a: a, b: b}',
...                 mydata,
...                 jmespath.Options(dict_cls=collections.OrderedDict))


>>> import jmespath
>>> parsed = jmespath.compile('{a: a, b: b}')
>>> parsed.search(mydata,
...               jmespath.Options(dict_cls=collections.OrderedDict))
```

JMESPath used to support a special case <span
class="title-ref">json-value</span> syntax to represent a JSON string
literal, but this was being deprecated following
[JEP-12](https://github.com/jmespath-community/jmespath.spec/blob/main/jep-012-raw-string-literals.md)
and its <span class="title-ref">raw-string</span> literal syntax.

``` python
>>> import jmespath
>>> jmespath.search("`foo`"', {})
jmespath.exceptions.LexerError: Bad jmespath expression: Bad token %s `foo`:
`foo`
^
```

While JMESPath Community now fully deprecates this legacy syntax of
providing a JSON literal string with elided double quotes, you can still
opt-in to parse legacy syntax, by specifying the
`enable_legacy_literals` flag to the `Options` object.

``` python
>>> import jmespath
>>> jmespath.search("`foo`"',
...                 mydata,
...                 jmespath.Options(enable_legacy_literals=True))
'foo'


>>> import jmespath
>>> parsed = jmespath.compile("`foo`",
...               jmespath.Options(enable_legacy_literals=True))
>>> parsed.search(mydata)
'foo'
```

### Custom Functions

The JMESPath language has numerous [built-in
functions](https://jmespath.site/main/#functions), but it is also
possible to add your own custom functions. Keep in mind that custom
function support in jmespath.py is experimental and the API may change
based on feedback.

**If you have a custom function that you've found useful, consider
submitting it to jmespath.site and propose that it be added to the
JMESPath language.** You can submit proposals
[here](https://github.com/jmespath-community/jmespath.spec/issues).

To create custom functions:

-   Create a subclass of `jmespath.functions.Functions`.
-   Create a method with the name `_func_<your function name>`.
-   Apply the `jmespath.functions.signature` decorator that indicates
    the expected types of the function arguments.
-   Provide an instance of your subclass in a `jmespath.Options` object.

Below are a few examples:

``` python
import jmespath
from jmespath import functions

# 1. Create a subclass of functions.Functions.
#    The function.Functions base class has logic
#    that introspects all of its methods and automatically
#    registers your custom functions in its function table.
class CustomFunctions(functions.Functions):

    # 2 and 3.  Create a function that starts with _func_
    # and decorate it with @signature which indicates its
    # expected types.
    # In this example, we're creating a jmespath function
    # called "unique_letters" that accepts a single argument
    # with an expected type "string".
    @functions.signature({'types': ['string']})
    def _func_unique_letters(self, s):
        # Given a string s, return a sorted
        # string of unique letters: 'ccbbadd' ->  'abcd'
        return ''.join(sorted(set(s)))

    # Here's another example.  This is creating
    # a jmespath function called "my_add" that expects
    # two arguments, both of which should be of type number.
    @functions.signature({'types': ['number']}, {'types': ['number']})
    def _func_my_add(self, x, y):
        return x + y

# 4. Provide an instance of your subclass in a Options object.
options = jmespath.Options(custom_functions=CustomFunctions())

# Provide this value to jmespath.search:
# This will print 3
print(
    jmespath.search(
        'my_add(`1`, `2`)', {}, options=options)
)

# This will print "abcd"
print(
    jmespath.search(
        'foo.bar | unique_letters(@)',
        {'foo': {'bar': 'ccbbadd'}},
        options=options)
)
```

Again, if you come up with useful functions that you think make sense in
the JMESPath language (and make sense to implement in all JMESPath
libraries, not just python), please let us know at
[jmespath.site](https://github.com/jmespath-community/jmespath.spec/discussions).

# Specification

If you'd like to learn more about the JMESPath language, you can check
out the [JMESPath tutorial](https://jmespath.site/main/#tutorial). Also
check out the [JMESPath examples
page](https://jmespath.site/main/#examples) for examples of more complex
jmespath queries.

The grammar is specified using ABNF, as described in
[RFC4234](http://www.ietf.org/rfc/rfc4234.txt). You can find the most up
to date [grammar for JMESPath
here](https://jmespath.site/main/#spec-grammar).

You can read the full [JMESPath specification
here](https://jmespath.site/main/#specification).

# Testing

In addition to the unit tests for the jmespath modules, there is a
`tests/compliance` directory that contains .json files with test cases.
This allows other implementations to verify they are producing the
correct output. Each json file is grouped by feature.

# Contributing

Clone this repository and run the following commands:

```sh
pip install pipx
source ~/.bashrc
pipx install poetry

git submodule update --init --checkout --recursive --force
./scripts/sync-tests

poetry install
poetry build
poetry run pytest
```

# Discuss

Join us on our [Gitter channel](https://gitter.im/jmespath/chat) if you
want to chat or if you have any questions.
