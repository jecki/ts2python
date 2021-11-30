.. ts2python documentation master file, created by
   sphinx-quickstart on Fri Oct  8 08:32:17 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. default-domain::py

Welcome to ts2python's documentation!
=====================================

ts2python is a transpiler that converts TypeScript-interfaces to Python
records like TypedDict and provides runtime json-validation against those
interfaces/TypedDicts. 

(In the future also other record structures like
pydantic or attr might be supported by ts2python as well.)

ts2python can be installed with::

    # pip install ts2python

ts2python is licensed under the Apache-2.0 open source license.
The source code can be cloned from:
`https://github.com/jecki/ts2python <https://github.com/jecki/ts2python>`_

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
