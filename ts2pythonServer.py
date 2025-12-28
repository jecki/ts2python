#!/usr/bin/env python3

"""ts2pythonServer.py - starts a server (if not already running) for the
                    compilation of ts2python
"""

import asyncio
import os
import sys

VERBOSE = False

assert sys.version_info >= (3, 6, 0), "DHParser.server requires at least Python-Version 3.6.0"

try:
    scriptdir, scriptname = os.path.split(os.path.realpath(__file__))
    scriptpath = os.path.abspath(scriptdir)
    servername = os.path.splitext(scriptname)[0]
except NameError:
    scriptdir = ''
    servername = 'DHParserServer'

STOP_SERVER_REQUEST_BYTES = b"__STOP_SERVER__"   # hardcoded in order to avoid import from DHParser.server
IDENTIFY_REQUEST = "identify()"
LOGGING_REQUEST = 'logging("")'
LOG_PATH = 'LOGS/'

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8890
ALTERNATIVE_PORTS = [8888, 8889, 8898, 8980, 8988, 8989]

DATA_RECEIVE_LIMIT = 262144
SERVER_REPLY_TIMEOUT = 20

KNOWN_HOST = ''  # if host and port are retrieved from a config file, their
KNOWN_PORT = -2  # values are stored to these global variables

config_filename_cache = ''


CONNECTION_TYPE = 'tcp'   # valid values: 'tcp', 'streams'
echo_file = None


def echo(msg: str):
    """Writes the message to stdout, or redirects it to a text file, in
    case the server is connected via IO-streams instead of tcp."""
    global CONNECTION_TYPE, echo_file
    if CONNECTION_TYPE == 'tcp':
        print(msg)
    elif CONNECTION_TYPE == 'streams':
        if echo_file is None or echo_file.closed:
            new_file_flag = echo_file is None
            echo_file = open('print.txt', 'a', encoding='utf-8')
            if new_file_flag:
                import atexit
                atexit.register(echo_file.close)
            import time
            t = time.localtime()
            echo_file.write("\n\nDate and Time: %i-%i-%i %i:%i\n\n" % t[:5])
        echo_file.write(msg)
        echo_file.write('\n')
        echo_file.flush()
    else:
        print('Unknown connectsion type: %s. Must either be streams or tcp.' % CONNECTION_TYPE)


def verbose(msg: str):
    """Prints an additional message if VERBOSE-flag is set"""
    global VERBOSE
    if VERBOSE:
        echo(msg)


def get_config_filename() -> str:
    """
    Returns the file name of a temporary config file that stores
    the host and port of the currently running server.
    """
    global config_filename_cache
    if config_filename_cache:
        return config_filename_cache

    def probe(dir_list) -> str:
        for tmpdir in dir_list:
            if os.path.exists(tmpdir) and os.path.isdir(tmpdir):
                return tmpdir
        return ''

    if sys.platform.find('win') >= 0:
        tmpdir = probe([r'C:\TEMP', r'C:\TMP', r'\TEMP', r'\TMP'])
    else:
        tmpdir = probe(['~/tmp', '/tmp', '/var/tmp', 'usr/tmp'])
    config_filename_cache = os.path.join(tmpdir, os.path.basename(__file__)) + '.cfg'
    return config_filename_cache


def retrieve_host_and_port():
    """
    Retrieve host and port from temporary config file or return default values
    for host and port, in case the temporary config file does not exist.
    """
    global DEFAULT_HOST, DEFAULT_PORT, KNOWN_HOST, KNOWN_PORT
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    cfg_filename = get_config_filename()
    try:
        with open(cfg_filename, 'r', encoding='utf-8') as f:
            host, ports = f.read().strip(' \n').split(' ')
            port = int(ports)
            if (host, port) != (KNOWN_HOST, KNOWN_PORT):
                verbose('Retrieved host and port value %s:%i from config file "%s".'
                      % (host, port, cfg_filename))
            KNOWN_HOST, KNOWN_PORT = host, port
    except FileNotFoundError:
        verbose('File "%s" does not exist. Using default values %s:%i for host and port.'
              % (cfg_filename, host, port))
    except ValueError:
        verbose('removing invalid config file: ' + cfg_filename)
        os.remove(cfg_filename)
    return host, port


def asyncio_run(coroutine):
    """Backward compatible version of Pyhon3.7's `asyncio.run()`"""
    if sys.version_info >= (3, 7, 0):
        return asyncio.run(coroutine)
    else:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coroutine)
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            finally:
                asyncio.set_event_loop(None)
                loop.close()


def json_rpc(func_name, params={}, ID=None) -> dict:
    """Generates a JSON-RPC-call for `func` with parameters `params`"""
    return {"jsonrpc": "2.0", "method": func_name, "params": params, "id": ID}


class ts2pythonCPUBoundTasks:
    def __init__(self, lsp_data: dict):
        from DHParser.lsp import gen_lsp_table
        self.lsp_data = lsp_data
        self.lsp_table = gen_lsp_table(self, prefix='lsp_')


class ts2pythonBlockingTasks:
    def __init__(self, lsp_data: dict):
        from DHParser.lsp import gen_lsp_table
        self.lsp_data = lsp_data
        self.lsp_table = gen_lsp_table(self, prefix='lsp_')


class ts2pythonLanguageServerProtocol:
    """
    For the specification and implementation of the language server protocol, see:
        https://code.visualstudio.com/api/language-extensions/language-server-extension-guide
        https://microsoft.github.io/language-server-protocol/
        https://langserver.org/
    """
    def __init__(self):
        from DHParser.lsp import gen_lsp_table
        self.lsp_data = {
            'processId': 0,
            'rootUri': '',
            'clientCapabilities': {},
            'serverInfo': { "name": "ts2python-Server", "version": "0.1" },
            'serverCapabilities': {}
        }
        self.connection = None
        self.cpu_bound = ts2pythonCPUBoundTasks(self.lsp_data)
        self.blocking = ts2pythonBlockingTasks(self.lsp_data)
        self.lsp_table = gen_lsp_table(self, prefix='lsp_')
        self.lsp_fulltable = self.lsp_table.copy()
        assert self.lsp_fulltable.keys().isdisjoint(self.cpu_bound.lsp_table.keys())
        self.lsp_fulltable.update(self.cpu_bound.lsp_table)
        assert self.lsp_fulltable.keys().isdisjoint(self.blocking.lsp_table.keys())
        self.lsp_fulltable.update(self.blocking.lsp_table)

    def connect(self, connection):
        self.connection = connection

    def lsp_initialize(self, **kwargs):
        # # This has been taken care of by DHParser.server.Server.lsp_verify_initialization()
        # if self.shared.initialized or self.shared.processId != 0:
        #     return {"code": -32002, "message": "Server has already been initialized."}
        # self.shared.shutdown = False
        self.lsp_data['processId'] = kwargs['processId']
        self.lsp_data['rootUri'] = kwargs['rootUri']
        self.lsp_data['clientCapabilities'] = kwargs['capabilities']
        return {'capabilities': self.lsp_data['serverCapabilities'],
                'serverInfo': self.lsp_data['serverInfo']}

    def lsp_custom(self, **kwargs):
        return kwargs

    def lsp_shutdown(self, **kwargs):
        self.lsp_data['processId'] = 0
        self.lsp_data['rootUri'] = ''
        self.lsp_data['clientCapabilities'] = {}
        return {}

    def batch_job(self, argstr: str):
        from ts2pythonParser import batch_process
        args = argstr.split(' ')
        indir, outdir = args[1], args[3]

        assert args[0] == '--in'
        assert args[2] == '--out'
        if not os.path.exists(outdir): os.mkdir(outdir)
        elif not os.path.isdir(outdir):
            return 'Output directory "%s" exists and is not a directory!' % outdir
        if not os.path.exists(indir):
            return 'Input directory "%s" does not exist!' % indir
        elif not os.path.isdir(indir):
            return 'Input place "%s" is not a directory!' % indir

        file_names = []
        for entry in args[4:]:
            if not os.path.isabs(entry):
                entry = os.path.abspath(os.path.join(indir, entry))
            if os.path.isdir(entry):
                for file in os.listdir(entry):
                    file_path = os.path.join(entry, file)
                    if os.path.isfile(file_path):
                        file_names.append(file_path)
                break  # allow at most one directory
            else:
                file_names.append(entry)
        exenv = self.connection.exec
        error_list = batch_process(file_names, outdir, submit_func=exenv.submit_as_process,
                                   log_func=self.connection.log)
        return error_list

    # def simply_compile(self, argstr):
    #     from ts2pythonParser import compile_src
    #     return compile_src(argstr)

    async def simply_compile(self, argstr: str):
        from functools import partial
        from ts2pythonParser import compile_src
        exenv = self.connection.exec
        if argstr[:2] != '--':
            return await exenv.loop.run_in_executor(
                exenv.process_executor, partial(compile_src, argstr))
        else:
            return await exenv.loop.run_in_executor(
                exenv.thread_executor, partial(self.batch_job, argstr))


def run_server(host, port, log_path=None):
    """
    Starts a new ts2pythonServer. If `port` is already occupied, different
    ports will be tried.
    """
    global KNOWN_HOST, KNOWN_PORT
    global scriptpath, servername

    from multiprocessing import set_start_method
    # 'forkserver' or 'spawn' required to avoid broken process pools
    if sys.platform.lower().startswith('linux') :  set_start_method('forkserver')
    else:  set_start_method('spawn')

    try:
        grammar_src = os.path.abspath(os.path.realpath(__file__)).replace('Server.py', '.ebnf')
    except NameError:
        grammar_src = ''
    if scriptpath and scriptpath not in sys.path:
        sys.path.append(scriptpath)
    try:
        from DHParser import versionnumber
    except (ImportError, ModuleNotFoundError):
        i = scriptdir.rfind("/DHParser/")
        if i >= 0:
            dhparserdir = scriptdir[:i + 10]  # 10 = len("/DHParser/")
            if dhparserdir not in sys.path:  sys.path.insert(0, dhparserdir)

    from DHParser.dsl import recompile_grammar
    if grammar_src and not recompile_grammar(grammar_src, force=False,
            notify=lambda: print('recompiling ' + grammar_src)):
        print('\nErrors while recompiling "%s":' % grammar_src +
              '\n--------------------------------------\n\n')
        with open('ts2python_ebnf_ERRORS.txt', 'r', encoding='utf-8') as f:
            print(f.read())
        sys.exit(1)

    from DHParser.server import Server, probe_tcp_server, StreamReaderProxy, StreamWriterProxy
    # from DHParser.lsp import gen_lsp_table

    ts2python_lsp = ts2pythonLanguageServerProtocol()
    lsp_table = ts2python_lsp.lsp_fulltable.copy()
    lsp_table.setdefault('default', ts2python_lsp.simply_compile)
    ts2python_server = Server(rpc_functions=lsp_table,
                        cpu_bound=ts2python_lsp.cpu_bound.lsp_table.keys(),
                        blocking=ts2python_lsp.blocking.lsp_table.keys(),
                        connection_callback=ts2python_lsp.connect,
                        server_name="ts2pythonServer",
                        strict_lsp=True)
    if log_path is not None:
        # echoing does not work with stream connections!
        ts2python_server.echo_log = True if port >= 0 and host else False
        msg = ts2python_server.start_logging(log_path.strip('" \''))
        if ts2python_server.echo_log:  echo(msg)

    if port < 0 or not host:
        # communication via streams instead of tcp server
        reader = StreamReaderProxy(sys.stdin)
        writer = StreamWriterProxy(sys.stdout)
        ts2python_server.run_stream_server(reader, writer)
        return

    cfg_filename = get_config_filename()
    overwrite = not os.path.exists(cfg_filename)
    ports = ALTERNATIVE_PORTS.copy() if port == DEFAULT_PORT else []
    if port in ports:
        ports.remove(port)
    ports.append(port)

    while ports:
        port = ports.pop()
        if (host, port) == (KNOWN_HOST, KNOWN_PORT):
            ident = asyncio_run(probe_tcp_server(host, port, SERVER_REPLY_TIMEOUT))
            if ident:
                if ident.endswith(servername):
                    echo('A server of type "%s" already exists on %s:%i.' % (servername, host, port)
                          + ' Use --port option to start a secondary server on a different port.')
                    sys.exit(1)
                if ports:
                    echo('"%s" already occupies %s:%i. Trying port %i' % (ident, host, port, ports[-1]))
                    continue
                else:
                    echo('"%s" already occupies %s:%i. No more ports to try.' % (ident, host, port))
                    sys.exit(1)
        if overwrite:
            try:
                with open(cfg_filename, 'w', encoding='utf-8') as f:
                    verbose('Storing host and port value %s:%i in file "%s".'
                          % (host, port, cfg_filename))
                    f.write(host + ' ' + str(port))
            except (PermissionError, IOError) as e:
                echo('%s: Could not write temporary config file: "%s"' % (str(e), cfg_filename))
                ports = []
        else:
            echo('Configuration file "%s" already existed and was not overwritten. '
                  'Use option "--port %i" to stop this server!' % (cfg_filename, port))
        try:
            echo('Starting server on %s:%i' % (host, port))
            ts2python_server.run_tcp_server(host, port)  # returns only after server has stopped!
            ports = []
        except OSError as e:
            if not (ports and e.errno == 98):
                echo(e)
                echo('Could not start server. Shutting down!')
                sys.exit(1)
            elif ports:
                echo('Could not start server on %s:%i. Trying port %s' % (host, port, ports[-1]))
            else:
                echo('Could not start server on %s:%i. No more ports to try.' % (host, port))
        finally:
            if not ports:
                echo('Server on %s:%i stopped' % (host, port))
                try:
                    os.remove(cfg_filename)
                    verbose('removing temporary config file: ' + cfg_filename)
                except FileNotFoundError:
                    pass


async def send_request(reader, writer, request, timeout=SERVER_REPLY_TIMEOUT) -> str:
    """Sends a request and returns the decoded response."""
    writer.write(request.encode() if isinstance(request, str) else request)
    try:
        data = await asyncio.wait_for(reader.read(DATA_RECEIVE_LIMIT), timeout)
    except asyncio.TimeoutError as e:
        echo('Server did not answer to "%s"-Request within %i seconds.'
              % (request, timeout))
        raise e
    return data.decode()


async def close_connection(writer):
    """Closes the communication-channel."""
    writer.close()
    if sys.version_info >= (3, 7, 0):
        await writer.wait_closed()


async def final_request(reader, writer, request, timeout=SERVER_REPLY_TIMEOUT) -> str:
    """Sends a (last) request and then closes the communication channel.
    Returns the decoded response to the request."""
    try:
        data = await send_request(reader, writer, request, timeout)
    finally:
        await close_connection(writer)
    return data


async def single_request(request, host, port, timeout=SERVER_REPLY_TIMEOUT) -> str:
    """Opens a connection, sends a single request, and closes the connection
    again before returning the decoded result."""
    try:
        reader, writer = await asyncio.open_connection(host, port)
    except ConnectionRefusedError:
        echo('No server running on: ' + host + ':' + str(port))
        sys.exit(1)
    try:
        result = await final_request(reader, writer, request, timeout)
    except asyncio.TimeoutError:
        sys.exit(1)
    return result


async def connect_to_daemon(host, port) -> tuple:
    """Opens a connections to the server on host, port. Returns the reader,
    writer and the string result of the identification-request."""
    global KNOWN_HOST, KNOWN_PORT, servername
    if sys.platform.find('win') < 0:
        delay = 0.05
        countdown = SERVER_REPLY_TIMEOUT / delay + 10
    else:
        delay = 0.05
        countdown = max(SERVER_REPLY_TIMEOUT, 5)
    ident, reader, writer = None, None, None
    cfg_filename = get_config_filename()
    save = (host, port)
    while countdown > 0:
        try:
            if (host, port) != (KNOWN_HOST, KNOWN_PORT):
                raise ValueError  # don't connect if host and port are not either
                # read from config-file or specified explicitly on the command line
            reader, writer = await asyncio.open_connection(host, port)
            try:
                ident = await send_request(reader, writer, IDENTIFY_REQUEST)
                if ident.find(servername) < 0:
                    ident = None
                    raise ValueError
                countdown = 0
            except (asyncio.TimeoutError, ValueError):
                echo('Server "%s" not found on %s:%i' % (servername, host, port))
                await close_connection(writer)
                reader, writer = None, None
                await asyncio.sleep(delay)
                countdown -= 1
                h, p = retrieve_host_and_port()
                if (h, p) != (host, port):
                    # try again with a different host and port
                    host, port = h, p
        except (ConnectionRefusedError, ValueError):
            await asyncio.sleep(delay)
            if os.path.exists(cfg_filename):
                host, port = retrieve_host_and_port()
            countdown -= 1
    if ident is not None and save != (host, port):
        echo('Server "%s" found on different port %i' % (servername, port))
    return reader, writer, ident


async def start_server_daemon(host, port, requests, timeout=SERVER_REPLY_TIMEOUT) -> list:
    """Starts a server in the background and opens a connections. Sends requests if
    given and returns a list of their results."""
    import subprocess

    ident, reader, writer = None, None, None
    if os.path.exists(get_config_filename()):
        reader, writer, ident = await connect_to_daemon(host, port)
    if ident is not None:
        if not requests:
            echo('Server "%s" already running on %s:%i' % (ident, host, port))
        else:
            verbose('Connection to server "%s" established.' % ident)
    else:
        try:
            if sys.platform.find('win') >= 0:  raise OSError
            subprocess.Popen([__file__, '--startserver', host, str(port)])
        except OSError:
            subprocess.Popen([sys.executable, __file__, '--startserver', host, str(port)])
        verbose('Server starting on %s:%i.' % (host, port))
        reader, writer, ident = await connect_to_daemon(host, port)
        if ident is None:
            echo('Could not start server or establish connection in time :-(')
            sys.exit(1)
        if not requests:
            echo('Connection to server "%s" established.' % ident)
        else:
            verbose('Connection to server "%s" established.' % ident)
    results = []
    for request in requests:
        assert request
        verbose("Sending request: '%s'" % str(request))
        results.append(await send_request(reader, writer, request, timeout))
    await close_connection(writer)
    verbose('Connection closed.')
    return results


def parse_logging_args(args):
    if args.logging or args.logging is None:
        global host, port
        if port >= 0 and host:
            echo = repr('ECHO_ON') if isinstance(args.startserver, list) else repr('ECHO_OFF')
        else:  # echoing does not work with stream connections!
            echo = repr('ECHO_OFF')
        if args.logging in ('OFF', 'STOP', 'NO', 'FALSE'):
            log_path = repr(None)
            echo = repr('ECHO_OFF')
        elif args.logging in ('ON', 'START', 'YES', 'TRUE'):
            log_path = repr(LOG_PATH)
        else:
            log_path = repr(LOG_PATH) if args.logging is None else repr(args.logging)
        request = LOGGING_REQUEST.replace('""', ", ".join((log_path, echo)))
        verbose('Logging to %s with call %s' % (log_path, request))
        return log_path, request
    else:
        return None, ''


def main():
    from argparse import ArgumentParser, REMAINDER
    parser = ArgumentParser(description="Setup and Control of a Server for processing ts2python-files.")
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('file', nargs='?')
    action_group.add_argument('-t', '--status', action='store_true',
                              help="displays the server's status, e.g. whether it is running")
    action_group.add_argument('-s', '--startserver', nargs='*', metavar=("HOST", "PORT"),
                              help="starts the server")
    action_group.add_argument('-d', '--startdaemon', action='store_true',
                              help="starts the server in the background")
    action_group.add_argument('-k', '--stopserver', action='store_true',
                              help="starts the server")
    action_group.add_argument('-r', '--stream', action='store_true', help="start stream server")
    parser.add_argument('-a', '--host', nargs=1, default=[''],
                        help='host name or IP-address of the server (default: 127.0.0.1)')
    parser.add_argument('-p', '--port', nargs=1, type=int, default=[-1],
                        help='port number of the server (default:8888)')
    parser.add_argument('-l', '--logging', nargs='?', metavar="ON|LOG_DIR|OFF", default='',
                        help='turns logging on (default) or off or writes log to a '
                             'specific directory (implies on)')
    parser.add_argument('-o', '--out', nargs='?',
                        help='output directory for batch processing')
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose messages")
    parser.add_argument('more_files', nargs='*')

    args = parser.parse_args()
    if args.verbose:
        VERBOSE = True

    host = args.host[0]
    port = int(args.port[0])

    if args.stream:
        CONNECTION_TYPE = 'streams'
        if port >= 0 or host:
            echo('Specifying host and port when using streams as transport does not make sense')
            sys.exit(1)
        log_path, _ = parse_logging_args(args)
        run_server('', -1, log_path)
        sys.exit(0)

    if port < 0 or not host:
        # if host and port have not been specified explicitly on the command
        # line, try to retrieve them from (temporary) config file or use
        # hard coded default values
        h, p = retrieve_host_and_port()
        if port < 0:
            port = p
        else:
            KNOWN_PORT = port  # we assume, the user knows what (s)he is doing...
        if not host:
            host = h
        else:
            KNOWN_HOST = host  # ...when explicitly requesting a particular host, port

    if args.status:
        result = asyncio_run(single_request(IDENTIFY_REQUEST, host, port, SERVER_REPLY_TIMEOUT))
        echo('Server ' + str(result) + ' running on ' + host + ':' + str(port))

    elif args.startserver is not None:
        portstr = None
        if len(args.startserver) == 1:
            host, portstr = args.startserver[0].split(':')
        elif len(args.startserver) == 2:
            host, portstr = args.startserver
        elif len(args.startserver) != 0:
            parser.error('Wrong number of arguments for "--startserver"!')
        if portstr is not None:
            try:
                port = int(portstr)
            except ValueError:
                parser.error('port must be a number!')
        log_path, _ = parse_logging_args(args)
        sys.exit(run_server(host, port, log_path))

    elif args.startdaemon:
        log_path, log_request = parse_logging_args(args)
        asyncio.run(start_server_daemon(host, port, [log_request] if log_request else []))

    elif args.stopserver:
        try:
            result = asyncio_run(single_request(STOP_SERVER_REQUEST_BYTES, host, port))
        except ConnectionRefusedError as e:
            echo(e)
            sys.exit(1)
        verbose(result)

    elif args.logging:
        log_path, request = parse_logging_args(args)
        verbose(asyncio_run(single_request(request, host, port)))

    elif args.file:
        timeout = SERVER_REPLY_TIMEOUT
        file_name = args.file
        if not file_name.endswith(')'):
            # argv does not seem to be a command (e.g. "identify()") but a file name or path
            if args.more_files or args.out or os.path.isdir(file_name):
                outdir = args.out or os.path.abspath('out')
                file_names = ' '. join(['--in', os.getcwd(), '--out', outdir, file_name]
                                       + args.more_files)
                timeout = 3600 * 24 * 365  # timout in batch mode: one year!
            else:
                file_names = os.path.abspath(file_name)
        log_path, log_request = parse_logging_args(args)
        requests = [log_request, file_names] if log_request else [file_names]
        result = asyncio_run(start_server_daemon(host, port, requests, timeout))[-1]
        if len(result) >= DATA_RECEIVE_LIMIT:
            echo(result, '...')
        else:
            echo(result)

    else:
        echo('Usages:\n'
             + '    python ts2pythonServer.py --startserver [--host host] [--port port] [--logging [ON|LOG_PATH|OFF]]\n'
             + '    python ts2pythonServer.py --startdaemon [--host host] [--port port] [--logging [ON|LOG_PATH|OFF]]\n'
             + '    python ts2pythonServer.py --stream\n'
             + '    python ts2pythonServer.py --stopserver\n'
             + '    python ts2pythonServer.py --status\n'
             + '    python ts2pythonServer.py --logging [ON|LOG_PATH|OFF]\n'
             + '    python ts2pythonServer.py FILENAME.dsl [--host host] [--port port]  [--logging [ON|LOG_PATH|OFF]]')
        sys.exit(1)


if __name__ == "__main__":
    main()
