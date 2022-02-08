#!/usr/bin/env python
# stolen from DHParser.testing

import collections
import concurrent.futures
import inspect
import os
import sys


def run_tests_in_class(cls_name, namespace, methods=()):
    """
    Runs tests in test-class `test` in the given namespace.

    """
    def instantiate(cls, nspace):
        """Instantiates class name `cls` within name-space `nspace` and
        returns the instance."""
        exec("instance = " + cls + "()", nspace)
        instance = nspace["instance"]
        setup = instance.setup if "setup" in dir(instance) else lambda : 0
        teardown = instance.teardown if "teardown" in dir(instance) else lambda : 0
        return instance, setup, teardown

    obj = None
    if methods:
        obj, setup, teardown = instantiate(cls_name, namespace)
        for name in methods:
            func = obj.__getattribute__(name)
            if callable(func):
                print("Running " + cls_name + "." + name)
                setup();  func();  teardown()
                # exec('obj.' + name + '()')
    else:
        obj, setup, teardown = instantiate(cls_name, namespace)
        for name in dir(obj):
            if name.lower().startswith("test"):
                func = obj.__getattribute__(name)
                if callable(func):
                    print("Running " + cls_name + "." + name)
                    setup();  func();  teardown()


def run_test_function(func_name, namespace):
    """
    Run the test-function `test` in the given namespace.
    """
    print("Running test-function: " + func_name)
    exec(func_name + '()', namespace)


def runner(tests, namespace, profile=False):
    """
    Runs all or some selected Python unit tests found in the
    namespace. To run all tests in a module, call
    ``runner("", globals())`` from within that module.

    Unit-Tests are either classes, the name of which starts with
    "Test" and methods, the name of which starts with "test" contained
    in such classes or functions, the name of which starts with "test".

    if `tests` is either the empty string or an empty sequence, runner
    checks sys.argv for specified tests. In case sys.argv[0] (i.e. the
    script's file name) starts with 'test' any argument in sys.argv[1:]
    (i.e. the rest of the command line) that starts with 'test' or
    'Test' is considered the name of a test function or test method
    (of a test-class) that shall be run. Test-Methods are specified in
    the form: class_name.method.name e.g. "TestServer.test_connection".

    :param tests: String or list of strings with the names of tests
        to run. If empty, runner searches by itself all objects the
        of which starts with 'test' and runs it (if its a function)
        or all of its methods that start with "test" if its a class
        plus the "setup" and "teardown" methods if they exist.

    :param namespace: The namespace for running the test, usually
        ``globals()`` should be used.

    :param profile: If True, the tests will be run with the profiler on.
        results will be displayed after the test-results. Profiling will
        also be turned on, if the parameter `--profile` has been provided
        on the command line.
    """
    test_classes = collections.OrderedDict()
    test_functions = []

    if tests:
        if isinstance(tests, str):
            tests = tests.split(' ')
        assert all(test.lower().startswith('test') for test in tests)
    else:
        tests = []
        if os.path.basename(sys.argv[0]).lower().startswith('test'):
            tests = [name for name in sys.argv[1:]
                     if os.path.basename(name.lower()).startswith('test')]
        if not tests:
            tests = [name for name in namespace.keys() if name.lower().startswith('test')]

    for name in tests:
        func_or_class, method = (name.split('.') + [''])[:2]
        if inspect.isclass(namespace[func_or_class]):
            if func_or_class not in test_classes:
                test_classes[func_or_class] = []
            if method:
                test_classes[func_or_class].append(method)
        elif inspect.isfunction(namespace[name]):
            test_functions.append(name)

    profile = profile or '--profile' in sys.argv
    if profile:
        import cProfile, pstats
        pr = cProfile.Profile()
        pr.enable()

    for cls_name, methods in test_classes.items():
        run_tests_in_class(cls_name, namespace, methods)

    for test in test_functions:
        run_test_function(test, namespace)

    if profile:
        pr.disable()
        st = pstats.Stats(pr)
        st.strip_dirs()
        st.sort_stats('time').print_stats(50)


def run_file(fname):
    dirname, fname = os.path.split(fname)
    if fname.lower().startswith('test_') and fname.endswith('.py'):
        print("RUNNING " + fname + " with: " + sys.version)
        # print('\nRUNNING UNIT TESTS IN: ' + fname)
        save = os.getcwd()
        os.chdir(dirname)
        exec('import ' + fname[:-3])
        runner('', eval(fname[:-3]).__dict__)
        os.chdir(save)


class SingleThreadExecutor(concurrent.futures.Executor):
    """SingleThreadExecutor is a replacement for
    concurrent.future.ProcessPoolExecutor and
    concurrent.future.ThreadPoolExecutor that executes any submitted
    task immediately in the submitting thread. This helps to avoid
    writing extra code for the case that multithreading or
    multiprocesssing has been turned off in the configuration. To do
    so is helpful for debugging.

    It is not recommended to use this in asynchronous code or code that
    relies on the submit() or map()-method of executors to return quickly.
    """
    def submit(self, fn, *args, **kwargs):
        future = concurrent.futures.Future()
        try:
            result = fn(*args, **kwargs)
            future.set_result(result)
        except BaseException as e:
            future.set_exception(e)
        return future


def run_path(path):
    """Runs all unit tests in `path`"""
    if os.path.isdir(path):
        sys.path.append(path)
        files = os.listdir(path)
        results = []
        with SingleThreadExecutor() as pool:
            for f in files:
                if f.find('test') >= 0 and f[-3:] == '.py':
                    results.append(pool.submit(run_file, os.path.join(path, f)))
                # run_file(f)  # for testing!
            assert results, f"No tests found in directory {os.path.abspath(path)}"
            concurrent.futures.wait(results)
            for r in results:
                try:
                    _ = r.result()
                except AssertionError as failure:
                    print(failure)

    else:
        path, fname = os.path.split(path)
        sys.path.append(path)
        run_file(fname)
    sys.path.pop()


def run_doctests():
    import doctest
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    ts2python_path = os.path.abspath(os.path.join(scriptdir, '..', 'ts2python'))
    sys.path.append(ts2python_path)
    import json_validation
    print('Running doctests of ts2python.json_validation')
    doctest.testmod(json_validation)


if __name__ == "__main__":
    path = '.'
    if len(sys.argv) > 1:
        path = sys.argv[1]
    if os.path.isdir(path):
        run_path(path)
    else:
        run_file(path)
    run_doctests()
    print()

