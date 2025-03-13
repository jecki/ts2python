#!/usr/bin/env python3

"""tst_ts2python_grammar.py - runs the unit tests for the ts2python-grammar
"""

import os
import sys

LOGGING = 'LOGS'
DEBUG = True
TEST_DIRNAME = 'tests_grammar'

try:
    scriptdir = os.path.dirname(os.path.realpath(__file__))
except NameError:
    scriptdir = ''
if scriptdir and scriptdir not in sys.path: sys.path.append(scriptdir)

try:
    from DHParser import versionnumber
except (ImportError, ModuleNotFoundError):
    i = scriptdir.rfind("/DHParser/")
    if i >= 0:
        dhparserdir = scriptdir[:i + 10]  # 10 = len("/DHParser/")
        if dhparserdir not in sys.path:  sys.path.insert(0, dhparserdir)


try:
    from DHParser.configuration import access_presets, set_preset_value, \
        finalize_presets, get_config_value
    from DHParser import dsl
    import DHParser.log
    from DHParser import testing
except ModuleNotFoundError:
    print('Could not import DHParser. Please adjust sys.path in file '
          '"%s" manually' % __file__)
    sys.exit(1)


def recompile_grammar(grammar_src, force):
    grammar_tests_dir = os.path.join(scriptdir, TEST_DIRNAME)
    testing.create_test_templates(grammar_src, grammar_tests_dir)
    # recompiles Grammar only if it has changed
    first_run = not os.path.exists(os.path.splitext(grammar_src)[0] + 'Parser.py')
    if not dsl.recompile_grammar(grammar_src, force=force,
            notify=lambda: print('recompiling ' + grammar_src)):
        msg = f'Errors while recompiling "%s":' % os.path.basename(grammar_src)
        print('\n'.join(['', msg, '-'*len(msg)]))
        error_path = os.path.join(grammar_src[:-5] + '_ebnf_MESSAGES.txt')
        with open(error_path, 'r', encoding='utf-8') as f:
            print(f.read())
        sys.exit(1)
    if first_run:  dsl.create_scripts(grammar_src)


def run_grammar_tests(fn_pattern, parser_factory, transformer_factory,
                      junctions=set(), targets=set(), serializations=set()):
    if fn_pattern.find('/') >= 0 or fn_pattern.find('\\') >= 0:
        testdir, fn_pattern = os.path.split(fn_pattern)
        if not testdir.startswith('/') or not testdir[1:2] == ':':
            testdir = os.path.abspath(testdir)
    else:
        testdir = os.path.join(scriptdir, TEST_DIRNAME)
    DHParser.log.start_logging(os.path.join(testdir, LOGGING))
    error_report = testing.grammar_suite(
        testdir, parser_factory, transformer_factory,
        fn_patterns=[fn_pattern], report='REPORT', verbose=True,
        junctions=junctions, show=targets, serializations=serializations)
    return error_report


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Runs all grammar-tests in "test_grammar/" '
        'or a given test - after (re-)creating the parser script if necessary.')
    parser.add_argument('files', nargs='*')
    parser.add_argument('-s', '--scripts', action='store_const', const='scripts',
        help="Creates a server- and an app-script. Existing scripts will not be overwritten!")
    parser.add_argument('--singlethread', action='store_const', const='singlethread',
                        help='Run tests in a single thread (recommended only for debugging)')
    parser.add_argument('-p', '--history', action='store_const', const='history',
                        help="Detailed logs for of the parsing-history for all tests.")
    parser.add_argument('-n', '--nohistory', action='store_const', const='nohistory',
                        help="Deprecated argument")
    parser.add_argument('-d', '--debug', action='store_const', const='debug',
                        help='Deprecated argument.')
    args = parser.parse_args()

    if args.debug is not None:
        print('Argument -d or --debug is deprecated! Parsing-histories of failed tests will '
              'be logged per default. Use -p or --history to log all tests.')
    if args.nohistory is not None:
        print('Argument -n or --nohistory is deprecated! Only parsing-histories of failed '
              'tests will be logged. Use -p or --history to log all tests.')

    from DHParser.configuration import read_local_config
    read_local_config(os.path.join(scriptdir, 'ts2python/ts2pythonParser.ini'))

    config_test_parallelization = get_config_value('test_parallelization')
    access_presets()
    if args.singlethread:
        set_preset_value('test_parallelization', False)
    elif not config_test_parallelization:
        print('Tests will be run in a single-thread, because test-multiprocessing '
              'has been turned off in configuration file.')
    set_preset_value('history_tracking', args.history)
    finalize_presets()

    if args.scripts:
        dsl.create_scripts(os.path.join(scriptdir, 'ts2python.ebnf'))

    if args.files:
        # if called with a single filename that is either an EBNF file or a known
        # test file type then use the given argument
        arg = args.files[0]
    else:
        # otherwise run all tests in the test directory
        arg = '*test*.ini'
    if arg.endswith('.ebnf'):
        recompile_grammar(arg, force=True)
    else:
        recompile_grammar(os.path.join(scriptdir, 'ts2python.ebnf'),
                          force=False)
        sys.path.append('.')
        from ts2pythonParser import parsing, ASTTransformation, \
            junctions, test_targets, serializations
        error_report = run_grammar_tests(arg, parsing.factory, ASTTransformation.factory,
                                         junctions, test_targets, serializations)
        if error_report:
            print('\n')
            print(error_report)
            sys.exit(1)
        print('ready.\n')
