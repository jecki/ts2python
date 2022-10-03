# ts2python

![](https://img.shields.io/pypi/v/ts2python) 
![](https://img.shields.io/pypi/status/ts2python) 
![](https://img.shields.io/pypi/pyversions/ts2python) 
![](https://img.shields.io/pypi/l/ts2python)

Python-interoperability for Typescript-Interfaces.
Transpiles TypeScript-Interface-definitions to Python 
TypedDicts, plus support for run-time type-checking 
of JSON-data.

## License and Source Code

ts2python is open source software under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0)

Copyright 2021 Eckhart Arnold <arnold@badw.de>, Bavarian Academy of Sciences and Humanities

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

The complete source-code of ts2python can be downloaded from the [its git-repository](https://github.com/jecki/ts2python).

## Purpose

When processing JSON data, as for example form a 
[JSON-RPC](https://www.jsonrpc.org/) call, with Python, it would
be helpful to have Python-definitions of the JSON-structures at
hand, in order to solicit IDE-Support, static type checking and,
potentially to enable structural validation at runtime. 

There exist different technologies for defining the structure of
JSON-data. Next to [JSON-schema](http://json-schema.org/), a 
de facto very popular technology for defining JSON-obejcts are
[Typescript-Interfaces](https://www.typescriptlang.org/docs/handbook/2/objects.html). 
For example, the 
[language server protocol](https://microsoft.github.io/language-server-protocol/specifications/specification-current/) 
defines the structure of the JSON-data exchanged between client 
and server with Typescript-Interfaces.

In order to enable structural validation on the Python-side, 
ts2python transpiles the typescript-interface definitions
to Python-data structure definitions, primarily, 
[TypedDicts](https://www.python.org/dev/peps/pep-0589/),
but with some postprocessing it can also be adjusted to
other popular models for records or data structures in
Python, e.g.
[pydantic](https://pydantic-docs.helpmanual.io/)-Classes
and the like.

ts2python aims to support translation of TypeScript-Interfaces on two
different tiers:

1. *Tier 1: Transpilation of passive data-structures*, that is, 
   Typescript-definition-files that contain only data definitions 
   and no function definitions and, in particular,
   only "passive" Typescript-Interface that define data-structures 
   but do not contain any methods.

2. *Tier 2: Tanspilation of active data-structures, function- 
   and method-definitions*, i.e. Translation of (almost) any
   Typescript-definition-file.

## Status

Presently, Tier 1 support, i.e. transpilation of passive data 
structures works quite well. So, for example, all Interfaces
from the
[language server protocol V3.16](https://microsoft.github.io/language-server-protocol/specifications/specification-3-16/) 
can be transpiled to Python Typed-Dicts. 

Tier 2 support is still very much work in progress. I am 
using "vscode.d.ts"-definition file as test case. Some things work,
but there are still some unsupported constructs and the Python
code emitted for features that go beyond Tier 1 may not even
be valid Python all the time! Please, keep that in mind.

The documentation presently only covers Tier 1 support. 


## Installation

ts2python can be installed from the command line with the command:

    $ pip install ts2python

ts2python requires the parsing-expression-grammar-framwork 
[DHParser](https://gitlab.lrz.de/badw-it/DHParser)
which will automatically be installed as a dependency by 
the `pip`-command. ts2python requires at least Python Version 3.8
to run. (If there is any interest, I might backport it to Python 3.6.)
However, the Python-code it produces is backwards compatible 
down to Python 3.6, if the 
[typing extensions](https://pypi.org/project/typing-extensions/) 
have been installed.

## Usage

In order to generate TypedDict-classes from Typescript-Interfaces,
run `ts2python` on the Typescript-Interface definitions:

    $ ts2python interfaces.ts

This generates a .py-file in same directory as the source
file that contains the TypedDict-classes and can simpy be 
imported in Python-Code:

    from interfaces import *

Json-data which adheres to a specific structure (no matter
whether defined on the typescript side via interfaces or
on the Python-side via TypedDicts) can easily be interchanged
and deserialized:

    import json
    request_msg: RequestMessage = json.loads(input_data)

The root-type (``RootMessage`` in the above example) can
be arbitrarily complex and deeply nested.


## Validation

ts2python ships support for runtime-type validation. While type
errors can be detected by static type checkers, runtime type 
validation can be useful when processing data from an outside
source which cannot statically be checked, like, for example,
json-data stemming from an RPC-call. ts2python runtime-type
validation can be invoked via dedicated functions or via
decorator as in this example:

    from ts2python.json_validation import TypedDict, type_check

    class Position(TypedDict, total=True):
        line: int
        character: int 

    class Range(TypedDict, total=True):
        start: Position
        end: Position

    @type_check
    def middle_line(rng: Range) -> Position:
        line = (rng['start']['line'] + rng['end']['line']) // 2
        character = 0
        return Position(line=line, character=character)

    data = {'start': {'line': 1, 'character': 1},
           'end': {'line': 8, 'character': 17}}
    assert middle_line(data) == {'line': 4, 'character': 0}

    malformed_data = {'start': 1, 'end': 8}
    middle_line(malformed_data)  # <- TypeError raised by @type_check 

With the type decorator the last call fails with a TypeError:

    TypeError: Parameter "rng" of function "middle_line" failed the type-check, because:
    Type error(s) in dictionary of type <class '__main__.Range'>:
    Field start: '1' is not of <class '__main__.Position'>, but of type <class 'int'>
    Field end: '8' is not of <class '__main__.Position'>, but of type <class 'int'>

Both the call and the return types can be validated.


## Full Documentation

See [ts2python.readthedocs.io](https://ts2python.readthedocs.io) for the comprehensive
documentation of ts2python


## Tests and Demonstration

The [git-repository of ts2python](https://github.com/jecki/ts2python) contains unit-tests 
as well as [doctests](https://docs.python.org/3/library/doctest.html).
After cloning ts2python from the git-repository with:

    $ git clone https://github.com/jecki/ts2python

the unit tests can be found in the `tests` subdirectory. 
Both the unit and the doctests can be run by changing to the 
`tests`-sub-directory and calling the `runner.py`-skript therein. 

    $ cd tests
    $ python runner.py

It is also possible to run the tests with [pytest](https://docs.pytest.org/) 
or [nose](https://nose.readthedocs.io), in case you have
either of theses testing-frameworks installed.

For a demonstration how the TypeScript-Interfaces are transpiled
to Python-code, run the `demo.sh`-script (or `demo.bat` on Windows)
in the "demo"-sub-directory or the ts2python-repository. 

Or, run the `tst_ts2python_grammar.py` in the ts2python-directory
and look up the grammar-test-reports in the "REPORT"-sub-directory 
of the "test_grammar"-subdirectory.
