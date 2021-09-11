# stolen from DHParser.testing

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

    Example::

        class TestSomething()
            def setup(self):
                pass
            def teardown(self):
                pass
            def test_something(self):
                pass

        if __name__ == "__main__":
            from DHParser.testing import runner
            runner("", globals())
    """
    test_classes = collections.OrderedDict()
    test_functions = []

    if tests:
        if isinstance(tests, str):
            tests = tests.split(' ')
        assert all(test.lower().startswith('test') for test in tests)
    else:
        tests = []
        if sys.argv[0].lower().startswith('test'):
            tests = [name for name in sys.argv[1:] if name.lower().startswith('test')]
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
    if fname.lower().startswith('test_') and fname.endswith('.py'):
        print("RUNNING " + fname)
        # print('\nRUNNING UNIT TESTS IN: ' + fname)
        exec('import ' + fname[:-3])
        runner('', eval(fname[:-3]).__dict__)


def run_path(path):
    """Runs all unit tests in `path`"""
    if os.path.isdir(path):
        sys.path.append(path)
        files = os.listdir(path)
        results = []
        with instantiate_executor(get_config_value('test_parallelization') and len(files) > 1,
                                  concurrent.futures.ProcessPoolExecutor) as pool:
            for f in files:
                results.append(pool.submit(run_file, f))
                # run_file(f)  # for testing!
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