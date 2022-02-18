.. ts2python documentation master file, created by
   sphinx-quickstart on Fri Oct  8 08:32:17 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. default-domain::py

ts2python Documentation
=======================

ts2python_ is a transpiler that converts `TypeScript interfaces`_ to Python_
records like TypedDict_ and provides runtime json_-validation against those
interfaces/TypedDicts. 

(In the future also other record structures like
pydantic_ or attr_ might be supported by ts2python as well.)

ts2python_ is licensed under the `Apache-2.0`_ open source license.
The source code can be cloned freely from:
`https://github.com/jecki/ts2python <https://github.com/jecki/ts2python/>`_

ts2python_ can be installed as usual with Python's package-manager "pip"::

    $ pip install ts2python

ts2python requires at least Python_ Version 3.6. The only dependency of
ts2python is the parser-generator DHParser_. For Python versions below 3.8
installing the `typing_extensions`_ is highly recommended, though.

Alternatively, you can just download the script `ts2PythonParser.py`_ for converting
Typescript source code consisting to interface definitions to Python modules from the
git-repository which runs without installing ts2python as long as DHParser_ has been installed.
Or, if you just interested in runtime type validation, you can just copy the module
`json_validation`_ from the git repository, which merely requires the `typing_extensions`_ to
be present.

Generating Python pendants for typescript interfaces is as simple as calling:

   $ ts2python interfaces.ts

and then importing the generated ``interfaces.py`` by:

   from interfaces import *

For every typescript interface in the ``interfaces.ts`` file the generated
Python module contains a TypedDict-class with the same name that defines
the same data structure as the typescript interface. Typescript data serialized
as json can simply be deserialized by Python-code as long as you know the
type of the root data structure beforehand, e.g.::

    import json
    request_msg: RequestMessage = json.loads(input_data)

The only requirement is that the root type of the json data is known beforehand.
Everything else simply falls into place.

Current Limitations
-------------------

Presently, ts2python is mostly limited to Typescript-Interfaces that do not
contain any methods. The language server-protocol-definitions can be transpiled
successfully.

However, as of now, most Typescript-header files, i.e. the
files ending with ".d.ts" cannot be transpiled, because support for
function headers, classes and interfaces with methods, ambient modules
and namespaces is still incomplete. This will be added in the future.


.. _ts2python:  https://github.com/jecki/ts2python/
.. _Typescript interfaces: https://www.typescriptlang.org/docs/handbook/2/objects.html
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
