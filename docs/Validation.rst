Runtime Validation
==================

With TypedDict, any static type checker that already supports
TypedDicts can be leveraged to check the classes generated
by ts2python.

While TypedDict are intended only for static type checking,
it would be desirable to use them for runtime type checking
in certain application cases such as the transfer of json
encoded data which may not be type-safe.
