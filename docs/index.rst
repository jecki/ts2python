.. ts2python documentation master file, created by
   sphinx-quickstart on Fri Oct  8 08:32:17 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. default-domain::py

ts2python Documentation
=======================

ts2python_ is a transpiler that converts `TypeScript-interfaces`_ to Python_
TypedDict_-classes and provides runtime json_-validation against those
interfaces/TypedDicts.

ts2python_ is licensed under the `Apache-2.0`_ open source license.
The source code can be cloned freely from:
`https://github.com/jecki/ts2python <https://github.com/jecki/ts2python/>`_

Installation
------------

ts2python_ can be installed as usual with Python's package-manager "pip"::

    $ pip install ts2python

The ts2python-transpiler requires at least Python_ Version 3.8 to run.
However, the output that ts2python produces is backwards compatible
with Python 3.7, unless otherwise specified (see below). The only
dependency of ts2python is the parser-generator DHParser_.

Generating Python-pendants for Typescript-interfaces is as simple as calling::

   $ ts2python interfaces.ts

and then importing the generated ``interfaces.py`` by::

   from interfaces import *

For every typescript interface in the ``interfaces.ts`` file the generated
Python module contains a TypedDict-class with the same name that defines
the same data structure as the Typescript-interface. Typescript-data serialized
as json can simply be deserialized by Python-code as long as you know the
type of the root data structure beforehand, e.g.::

    import json
    request_msg: RequestMessage = json.loads(input_data)

The only requirement is that the root-type of the json-data is known beforehand.
Everything else simply falls into place.

Backwards compatibility
-----------------------

ts2python tries to be as backwards compatible as possible. To run ts2python you
need at least Python version 3.8. The code ts2python generates is backwards
compatible down to version 3.7. If you do not need to be compatible with older
versions, you can use the --compatibility [VERSION] switch to generate code
for newer versions only, e.g.::

   $ ts2python --compatibility 3.11 [FILENAME.ts]

Usually, this code is somewhat cleaner than the fully
compatible code. Also, certain features like ``type``-statments (Python 3.12 and
above) or the ``ReadOnly``-qualifier (Python 3.13 and higher) are only available
at higher compatibility levels!
In order to achieve full conformity with most type-checkers, it is advisable
to use compatibility level 3.11 and also add the ``-a toplevel`` switch
to always turn anonymous TypeScript-interfaces into top-level classes, rather
than locally defined classes. Local classes are not allowed for Python TypedDicts,
although they work perfectly well - except that type-checkers like pylance
emit an error-message.

With compatibility-level 3.11 and above, the generated code does not need to
use ts2python's "typeddict_shim"-compatibility layer, any more. This greatly
simplifies the import-block at the beginning of the generated code and
eliminates one of two dependencies of the generated code on the ts2python-package.

The other remaining dependency "singledispatch_shim" can be removed from the
generated code by hand, if there are no single-dispatch functions in the
code that dispatch on a forward-referenced type, i.e. a type that is denoted
in the code by a string containing the type-name rather than the type-name
directly. (It's a current limitation of functools.singledispatch that it
cannot handle forward references.)

Command-line switches
---------------------

The Python output of ts2pythonParser can be controlled by the following
command line-switches:

* ``-c`` followed by a Python Version-number, e.g. ``-c 3.12``

*  ``-p`` followed by a comma separated list of `PEP`_-numbers, e.g.
   ``-p 563,601``. Supported PEPs are:

   * `435`_  - use Enums (Python 3.4)
   * `563`_  - use postponed evaluation (Python 3.7)
   * `584`_ or `586`_  - use Literal type (Python 3.8)
   * `604`_  - use type union (Python 3.10)
   * `613`_  - use explicit type alias (Python 3.10 - 3.11)
   * `646`_  - use variadic Generics (Python 3.11)
   * `649`_ or `749`_ - assume deferred type evaluation (Python 3.14)
   * `655`_  - use NotRequired instead of Optional (Python3.11)
   * `695`_  - use type parameters (Python 3.12)
   * `705`_  - allow ReadOnly (Python 3.13)

   Setting a Python Version-Number with the ``-c`` switch also
   automatically sets all PEPs
   that have been implemented with that version, except for PEP `563`_ which
   must be set explicitly with the ``-p 563`` switch as this concerns an
   optional feature for Python-Versions 3.7-3.12 which will be turned on
   with the ``from future import __annotation__`` statement at the beginnig
   of the generated source code.

* ``-k`` preserves Typescript-multiline comments and adds them as
  Python-comments to the generated source-code

* ``-a`` followed by one of the four possible keywords ``local`` (default),
  ``toplevel``, ``functional``, ``type``. These are four different styles
  for transpiling anonymous interfaces. The default rule ``local`` is not
  strictly conformant with the type-rules for TypedDicts. For full type-checker
  conformance use ``toplevel``. The other two keywords, "functional" and "type"
  should be considered as experimental as they have seen little testing.

* ``-o`` followed by the name of an output-directory for the generated Python
  code. If an output-directory is chosen the results will be written as files
  to this directory, rather than printed to the console (stdout).


Current Limitations
-------------------

Presently, ts2python is mostly limited to Typescript-Interfaces that do not
contain any methods. The language server-protocol-definitions can be transpiled
successfully.

Hacking ts2python
-----------------

Hacking ts2python is not easy. (Sorry!) The reason is that ts2python
was primarily designed for a relatively limited application case, i.e.
transpiling interface definitions. In order to keep things simple, the
abstract syntax tree (AST) from the TypeScript source is directly converted
to Python code, rather than transforming the TypeScript-AST to a Python-AST
first.

Adding such a tree-to-tree-transformation before the Python code
generation stage certainly would have made sense -
among other things, because some components need to be re-ordered,
since Python does not know anonymous classes/interfaces.
However, for the above mentioned restricted purpose this appeared to me like
overengineering. Meanwhile, I have come to regret that,
because it makes adding more features harder.

In order to keep track of code snippets
that must be reordered or of names and scopes that need to be completed
or filled in later or, more generally, for any task that cannot be
completed locally, when transforming a particular node of the AST,
the present implementation keeps several different stacks in
instance-variables of the ts2pythonCompiler-object, namely,
``known_types``, ``local_classes``, ``base_classes``, ``obj_name``,
``scope_type``, ``optional_keys``. Lookout for where those stacks are used
when you to change something in the ts2python-source yourself!

.. _ts2python:  https://github.com/jecki/ts2python/
.. _Typescript-interfaces: https://www.typescriptlang.org/docs/handbook/2/objects.html
.. _TypedDict: https://www.python.org/dev/peps/pep-0589/
.. _json: https://www.json.org/
.. _Apache-2.0: https://www.apache.org/licenses/LICENSE-2.0
.. _Python: https://www.python.org/
.. _DHParser: https://gitlab.lrz.de/badw-it/DHParser
.. _pydantic: https://pydantic-docs.helpmanual.io/
.. _attr: https://www.attrs.org/
.. _ts2PythonParser.py: https://github.com/jecki/ts2python/blob/main/ts2pythonParser.py
.. _json_validation: https://github.com/jecki/ts2python/blob/main/ts2python/json_validation.py
.. _typing_extensions: https://github.com/python/typing/blob/master/typing_extensions/README.rst
.. _PEP: https://peps.python.org/
.. _435: https://peps.python.org/pep-0435/
.. _563: https://peps.python.org/pep-0563/
.. _584: https://peps.python.org/pep-0584/
.. _586: https://peps.python.org/pep-0586/
.. _604: https://peps.python.org/pep-0604/
.. _613: https://peps.python.org/pep-0613/
.. _646: https://peps.python.org/pep-0646/
.. _649: https://peps.python.org/pep-0649/
.. _655: https://peps.python.org/pep-0655/
.. _695: https://peps.python.org/pep-0695/
.. _705: https://peps.python.org/pep-0705/
.. _749: https://peps.python.org/pep-0749/

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   BasicUsage.rst
   Mapping.rst
   Validation.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
