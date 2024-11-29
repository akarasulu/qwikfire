"""
This type stub file was generated by pyright.
"""

import platform
from types import ModuleType
from typing import Any, Dict, Type, Union

"""
https://sh.readthedocs.io/en/latest/
https://github.com/amoffat/sh
"""
__version__ = ...
__project_url__ = ...
if "windows" in platform.system().lower(): ...
TEE_STDOUT = ...
TEE_STDERR = ...
DEFAULT_ENCODING = ...
IS_MACOS = ...
SH_LOGGER_NAME = ...
RUNNING_TESTS = ...
FORCE_USE_SELECT = ...
PUSHD_LOCK = ...

def get_num_args(fn):  # -> int:
    ...

_unicode_methods = ...
HAS_POLL = ...
POLLER_EVENT_READ = ...
POLLER_EVENT_WRITE = ...
POLLER_EVENT_HUP = ...
POLLER_EVENT_ERROR = ...

class PollPoller:
    def __init__(self) -> None: ...
    def __nonzero__(self):  # -> bool:
        ...
    def __len__(self):  # -> int:
        ...
    def register_read(self, f):  # -> None:
        ...
    def register_write(self, f):  # -> None:
        ...
    def register_error(self, f):  # -> None:
        ...
    def unregister(self, f):  # -> None:
        ...
    def poll(self, timeout):  # -> list[Any]:
        ...

class SelectPoller:
    def __init__(self) -> None: ...
    def __nonzero__(self):  # -> bool:
        ...
    def __len__(self):  # -> int:
        ...
    def register_read(self, f):  # -> None:
        ...
    def register_write(self, f):  # -> None:
        ...
    def register_error(self, f):  # -> None:
        ...
    def unregister(self, f):  # -> None:
        ...
    def poll(self, timeout):  # -> list[Any]:
        ...

Poller: Union[Type[SelectPoller], Type[PollPoller]] = ...
if HAS_POLL and not FORCE_USE_SELECT:
    Poller = ...

class ForkException(Exception):
    def __init__(self, orig_exc) -> None: ...

class ErrorReturnCodeMeta(type):
    """a metaclass which provides the ability for an ErrorReturnCode (or
    derived) instance, imported from one sh module, to be considered the
    subclass of ErrorReturnCode from another module.  this is mostly necessary
    in the tests, where we do assertRaises, but the ErrorReturnCode that the
    program we're testing throws may not be the same class that we pass to
    assertRaises
    """
    def __subclasscheck__(self, o):  # -> Literal[True]:
        ...

class ErrorReturnCode(Exception):
    __metaclass__ = ErrorReturnCodeMeta
    truncate_cap = ...
    def __reduce__(self):  # -> tuple[type[Self], tuple[Any, Any, Any, bool]]:
        ...
    def __init__(self, full_cmd, stdout, stderr, truncate=...) -> None: ...

class SignalException(ErrorReturnCode): ...

class TimeoutException(Exception):
    """the exception thrown when a command is killed because a specified
    timeout (via _timeout or .wait(timeout)) was hit"""
    def __init__(self, exit_code, full_cmd) -> None: ...

SIGNALS_THAT_SHOULD_THROW_EXCEPTION = ...

class CommandNotFound(AttributeError): ...

rc_exc_regex = ...
rc_exc_cache: Dict[str, Type[ErrorReturnCode]] = ...
SIGNAL_MAPPING = ...

def get_exc_from_name(name):  # -> type[ErrorReturnCode] | type[__class_ErrorReturnCodeMeta] | None:
    """takes an exception name, like:

        ErrorReturnCode_1
        SignalException_9
        SignalException_SIGHUP

    and returns the corresponding exception.  this is primarily used for
    importing exceptions from sh into user code, for instance, to capture those
    exceptions"""
    ...

def get_rc_exc(rc):  # -> type[ErrorReturnCode] | type[__class_ErrorReturnCodeMeta]:
    """takes a exit code or negative signal number and produces an exception
    that corresponds to that return code.  positive return codes yield
    ErrorReturnCode exception, negative return codes yield SignalException

    we also cache the generated exception so that only one signal of that type
    exists, preserving identity"""
    ...

_old_glob = ...

class GlobResults(list):
    def __init__(self, path, results) -> None: ...

def glob(path, *args, **kwargs):  # -> GlobResults:
    ...
def canonicalize(path): ...
def resolve_command_path(program):  # -> None:
    ...
def resolve_command(name, command_cls, baked_args=...):  # -> None:
    ...

class Logger:
    """provides a memory-inexpensive logger.  a gotcha about python's builtin
    logger is that logger objects are never garbage collected.  if you create a
    thousand loggers with unique names, they'll sit there in memory until your
    script is done.  with sh, it's easy to create loggers with unique names if
    we want our loggers to include our command arguments.  for example, these
    are all unique loggers:

            ls -l
            ls -l /tmp
            ls /tmp

    so instead of creating unique loggers, and without sacrificing logging
    output, we use this class, which maintains as part of its state, the logging
    "context", which will be the very unique name.  this allows us to get a
    logger with a very general name, eg: "command", and have a unique name
    appended to it via the context, eg: "ls -l /tmp" """
    def __init__(self, name, context=...) -> None: ...
    @staticmethod
    def sanitize_context(context):  # -> Literal['']:
        ...
    def get_child(self, name, context):  # -> Logger:
        ...
    def info(self, msg, *a):  # -> None:
        ...
    def debug(self, msg, *a):  # -> None:
        ...
    def error(self, msg, *a):  # -> None:
        ...
    def exception(self, msg, *a):  # -> None:
        ...

def default_logger_str(cmd, call_args, pid=...):  # -> str:
    ...

class RunningCommand:
    """this represents an executing Command object.  it is returned as the
    result of __call__() being executed on a Command instance.  this creates a
    reference to a OProc instance, which is a low-level wrapper around the
    process that was exec'd

    this is the class that gets manipulated the most by user code, and so it
    implements various convenience methods and logical mechanisms for the
    underlying process.  for example, if a user tries to access a
    backgrounded-process's stdout/err, the RunningCommand object is smart enough
    to know to wait() on the process to finish first.  and when the process
    finishes, RunningCommand is smart enough to translate exit codes to
    exceptions."""

    _OProc_attr_allowlist = ...
    def __init__(self, cmd, call_args, stdin, stdout, stderr) -> None: ...
    def wait(self, timeout=...):  # -> Self:
        """waits for the running command to finish.  this is called on all
        running commands, eventually, except for ones that run in the background

        if timeout is a number, it is the number of seconds to wait for the process to
        resolve. otherwise block on wait.

        this function can raise a TimeoutException, either because of a `_timeout` on
        the command itself as it was
        launched, or because of a timeout passed into this method.
        """
        ...

    def is_alive(self):  # -> bool:
        """returns whether or not we're still alive. this call has side-effects on
        OProc"""
        ...

    def handle_command_exit_code(self, code):  # -> None:
        """here we determine if we had an exception, or an error code that we
        weren't expecting to see.  if we did, we create and raise an exception
        """
        ...

    @property
    def stdout(self) -> bytes: ...
    @property
    def stderr(self) -> bytes: ...
    @property
    def exit_code(self) -> int: ...
    def __len__(self):  # -> int:
        ...
    def __enter__(self):  # -> None:
        """we don't actually do anything here because anything that should have
        been done would have been done in the Command.__call__ call.
        essentially all that has to happen is the command be pushed on the
        prepend stack."""
        ...

    def __iter__(self):  # -> Self:
        ...
    def __next__(self):  # -> int:
        """allow us to iterate over the output of our command"""
        ...

    def __await__(self):  # -> Generator[Any, Any, str]:
        ...
    def __aiter__(self):  # -> Self:
        ...
    async def __anext__(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb):  # -> None:
        ...
    def __str__(self) -> str: ...
    def __eq__(self, other) -> bool: ...
    def __contains__(self, item):  # -> bool:
        ...
    def __getattr__(self, p):  # -> Any:
        ...
    def __repr__(self):  # -> str:
        ...
    def __long__(self):  # -> int:
        ...
    def __float__(self):  # -> float:
        ...
    def __int__(self) -> int: ...

def output_redirect_is_filename(out):  # -> bool:
    ...
def get_prepend_stack():  # -> Any | list[Any]:
    ...
def special_kwarg_validator(passed_kwargs, merged_kwargs, invalid_list):  # -> list[Any]:
    ...
def get_fileno(ob):  # -> Any | int | None:
    ...
def ob_is_fd_based(ob):  # -> bool:
    ...
def ob_is_tty(ob):  # -> bool:
    """checks if an object (like a file-like object) is a tty."""
    ...

def ob_is_pipe(ob):  # -> bool:
    ...
def output_iterator_validator(passed_kwargs, merged_kwargs):  # -> list[Any]:
    ...
def tty_in_validator(passed_kwargs, merged_kwargs):  # -> list[Any]:
    ...
def fg_validator(passed_kwargs, merged_kwargs):  # -> list[Any]:
    """fg is not valid with basically every other option"""
    ...

def bufsize_validator(passed_kwargs, merged_kwargs):  # -> list[Any]:
    """a validator to prevent a user from saying that they want custom
    buffering when they're using an in/out object that will be os.dup'ed to the
    process, and has its own buffering.  an example is a pipe or a tty.  it
    doesn't make sense to tell them to have a custom buffering, since the os
    controls this."""
    ...

def env_validator(passed_kwargs, merged_kwargs):  # -> list[Any]:
    """a validator to check that env is a dictionary and that all environment variable
    keys and values are strings. Otherwise, we would exit with a confusing exit code
    255."""
    ...

class Command:
    """represents an un-run system program, like "ls" or "cd".  because it
    represents the program itself (and not a running instance of it), it should
    hold very little state.  in fact, the only state it does hold is baked
    arguments.

    when a Command object is called, the result that is returned is a
    RunningCommand object, which represents the Command put into an execution
    state."""

    thread_local = ...
    RunningCommandCls = RunningCommand
    _call_args: Dict[str, Any] = ...
    _kwarg_validators = ...
    def __init__(self, path, search_paths=...) -> None: ...
    def __getattribute__(self, name):  # -> Any:
        ...
    def bake(self, *args, **kwargs):  # -> Self:
        """returns a new Command object after baking(freezing) the given
        command arguments which are used automatically when its exec'ed

        special keyword arguments can be temporary baked and additionally be
        overridden in __call__ or in subsequent bakes (basically setting
        defaults)"""
        ...

    def __str__(self) -> str: ...
    def __eq__(self, other) -> bool: ...
    def __repr__(self):  # -> str:
        ...
    def __enter__(self):  # -> None:
        ...
    def __exit__(self, exc_type, exc_val, exc_tb):  # -> None:
        ...
    def __call__(self, *args, **kwargs):  # -> str | RunningCommandCls | None:
        ...

def compile_args(a, kwargs, sep, prefix):  # -> list[Any]:
    """takes args and kwargs, as they were passed into the command instance
    being executed with __call__, and compose them into a flat list that
    will eventually be fed into exec.  example:

    with this call:

        sh.ls("-l", "/tmp", color="never")

    this function receives

        args = ['-l', '/tmp']
        kwargs = {'color': 'never'}

    and produces

        ['-l', '/tmp', '--color=geneticnever']

    """
    ...

def setwinsize(fd, rows_cols):  # -> None:
    """set the terminal size of a tty file descriptor.  borrowed logic
    from pexpect.py"""
    ...

def construct_streamreader_callback(process, handler):  # -> Callable[..., Any]:
    """here we're constructing a closure for our streamreader callback.  this
    is used in the case that we pass a callback into _out or _err, meaning we
    want to our callback to handle each bit of output

    we construct the closure based on how many arguments it takes.  the reason
    for this is to make it as easy as possible for people to use, without
    limiting them.  a new user will assume the callback takes 1 argument (the
    data).  as they get more advanced, they may want to terminate the process,
    or pass some stdin back, and will realize that they can pass a callback of
    more args"""
    ...

def get_exc_exit_code_would_raise(
    exit_code, ok_codes, sigpipe_ok
):  # -> type[ErrorReturnCode] | type[__class_ErrorReturnCodeMeta] | None:
    ...
def handle_process_exit_code(exit_code) -> int:
    """this should only ever be called once for each child process"""
    ...

def no_interrupt(syscall, *args, **kwargs):
    """a helper for making system calls immune to EINTR"""
    ...

class OProc:
    """this class is instantiated by RunningCommand for a command to be exec'd.
    it handles all the nasty business involved with correctly setting up the
    input/output to the child process.  it gets its name for subprocess.Popen
    (process open) but we're calling ours OProc (open process)"""

    _default_window_size = ...
    STDOUT = ...
    STDERR = ...
    def __init__(self, command, parent_log, cmd, stdin, stdout, stderr, call_args, pipe, process_assign_lock) -> None:
        """
        cmd is the full list of arguments that will be exec'd.  it includes the program
        name and all its arguments.

        stdin, stdout, stderr are what the child will use for standard input/output/err.

        call_args is a mapping of all the special keyword arguments to apply to the
        child process.
        """
        ...

    def __repr__(self):  # -> str:
        ...
    def change_in_bufsize(self, buf):  # -> None:
        ...
    def change_out_bufsize(self, buf):  # -> None:
        ...
    def change_err_bufsize(self, buf):  # -> None:
        ...
    @property
    def stdout(self) -> bytes: ...
    @property
    def stderr(self) -> bytes: ...
    def get_pgid(self):  # -> int:
        """return the CURRENT group id of the process. this differs from
        self.pgid in that this reflects the current state of the process, where
        self.pgid is the group id at launch"""
        ...

    def get_sid(self):  # -> int:
        """return the CURRENT session id of the process. this differs from
        self.sid in that this reflects the current state of the process, where
        self.sid is the session id at launch"""
        ...

    def signal_group(self, sig):  # -> None:
        ...
    def signal(self, sig):  # -> None:
        ...
    def kill_group(self):  # -> None:
        ...
    def kill(self):  # -> None:
        ...
    def terminate(self):  # -> None:
        ...
    def is_alive(
        self,
    ):  # -> tuple[Literal[False], int] | tuple[Literal[False], Never] | tuple[Literal[True], None] | tuple[Literal[False], int | None]:
        """polls if our child process has completed, without blocking.  this
        method has side-effects, such as setting our exit_code, if we happen to
        see our child exit while this is running"""
        ...

    def wait(self):  # -> int:
        """waits for the process to complete, handles the exit code"""
        ...

def input_thread(log, stdin, is_alive, quit_thread, close_before_term):  # -> None:
    """this is run in a separate thread.  it writes into our process's
    stdin (a streamwriter) and waits the process to end AND everything that
    can be written to be written"""
    ...

def event_wait(ev, timeout=...): ...
def background_thread(timeout_fn, timeout_event, handle_exit_code, is_alive, quit_thread):  # -> None:
    """handles the timeout logic"""
    ...

def output_thread(
    log, stdout, stderr, timeout_event, is_alive, quit_thread, stop_output_event, output_complete
):  # -> None:
    """this function is run in a separate thread.  it reads from the
    process's stdout stream (a streamreader), and waits for it to claim that
    its done"""
    ...

class DoneReadingForever(Exception): ...
class NotYetReadyToRead(Exception): ...

def determine_how_to_read_input(
    input_obj,
):  # -> tuple[Callable[[], Any], Literal['queue', 'callable', 'file descriptor', 'string', 'bytes', 'generator', 'None', 'general iterable']]:
    """given some kind of input object, return a function that knows how to
    read chunks of that input object.

    each reader function should return a chunk and raise a DoneReadingForever
    exception, or return None, when there's no more data to read

    NOTE: the function returned does not need to care much about the requested
    buffering type (eg, unbuffered vs newline-buffered).  the StreamBufferer
    will take care of that.  these functions just need to return a
    reasonably-sized chunk of data."""
    ...

def get_queue_chunk_reader(stdin):  # -> Callable[[], Any]:
    ...
def get_callable_chunk_reader(stdin):  # -> Callable[[], Any]:
    ...
def get_iter_string_reader(stdin):  # -> Callable[[], Any]:
    """return an iterator that returns a chunk of a string every time it is
    called.  notice that even though bufsize_type might be line buffered, we're
    not doing any line buffering here.  that's because our StreamBufferer
    handles all buffering.  we just need to return a reasonable-sized chunk."""
    ...

def get_iter_chunk_reader(stdin):  # -> Callable[[], Any]:
    ...
def get_file_chunk_reader(stdin):  # -> Callable[[], Any]:
    ...
def bufsize_type_to_bufsize(bf_type):  # -> Literal[1024, 1]:
    """for a given bufsize type, return the actual bufsize we will read.
    notice that although 1 means "newline-buffered", we're reading a chunk size
    of 1024.  this is because we have to read something.  we let a
    StreamBufferer instance handle splitting our chunk on newlines"""
    ...

class StreamWriter:
    """StreamWriter reads from some input (the stdin param) and writes to a fd
    (the stream param).  the stdin may be a Queue, a callable, something with
    the "read" method, a string, or an iterable"""
    def __init__(self, log, stream, stdin, bufsize_type, encoding, tty_in) -> None: ...
    def fileno(self):  # -> Any:
        """defining this allows us to do poll on an instance of this
        class"""
        ...

    def write(self):  # -> bool | None:
        """attempt to get a chunk of data to write to our child process's
        stdin, then write it.  the return value answers the questions "are we
        done writing forever?" """
        ...

    def close(self):  # -> None:
        ...

def determine_how_to_feed_output(
    handler, encoding, decode_errors
):  # -> tuple[Callable[..., Any] | Callable[..., Literal[False]], Callable[[], None]]:
    ...
def get_fd_chunk_consumer(handler, decode_errors):  # -> tuple[Callable[..., Literal[False]], Callable[[], None]]:
    ...
def get_file_chunk_consumer(handler, decode_errors):  # -> tuple[Callable[..., Literal[False]], Callable[[], None]]:
    ...
def get_callback_chunk_consumer(handler, encoding, decode_errors):  # -> tuple[Callable[..., Any], Callable[[], None]]:
    ...
def get_cstringio_chunk_consumer(handler):  # -> tuple[Callable[..., Literal[False]], Callable[[], None]]:
    ...
def get_stringio_chunk_consumer(
    handler, encoding, decode_errors
):  # -> tuple[Callable[..., Literal[False]], Callable[[], None]]:
    ...

class StreamReader:
    """reads from some output (the stream) and sends what it just read to the
    handler."""
    def __init__(
        self, log, stream, handler, buffer, bufsize_type, encoding, decode_errors, pipe_queue=..., save_data=...
    ) -> None: ...
    def fileno(self):  # -> Any:
        """defining this allows us to do poll on an instance of this
        class"""
        ...

    def close(self):  # -> None:
        ...
    def write_chunk(self, chunk):  # -> None:
        ...
    def read(self):  # -> Literal[True] | None:
        ...

class StreamBufferer:
    """this is used for feeding in chunks of stdout/stderr, and breaking it up
    into chunks that will actually be put into the internal buffers.  for
    example, if you have two processes, one being piped to the other, and you
    want that, first process to feed lines of data (instead of the chunks
    however they come in), OProc will use an instance of this class to chop up
    the data and feed it as lines to be sent down the pipe"""
    def __init__(self, buffer_type, encoding=..., decode_errors=...) -> None: ...
    def change_buffering(self, new_type):  # -> None:
        ...
    def process(self, chunk):  # -> list[Any]:
        ...
    def flush(self):  # -> bytes:
        ...

def with_lock(lock):  # -> Callable[..., Callable[..., _GeneratorContextManager[None]]]:
    ...
@with_lock(PUSHD_LOCK)
def pushd(path):  # -> Generator[None, Any, None]:
    """pushd changes the actual working directory for the duration of the
    context, unlike the _cwd arg this will work with other built-ins such as
    sh.glob correctly"""
    ...

class Environment(dict):
    """this allows lookups to names that aren't found in the global scope to be
    searched for as a program name.  for example, if "ls" isn't found in this
    module's scope, we consider it a system program and try to find it.

    we use a dict instead of just a regular object as the base class because the
    exec() statement used in the run_repl requires the "globals" argument to be a
    dictionary"""

    allowlist = ...
    def __init__(self, globs, baked_args=...) -> None:
        """baked_args are defaults for the 'sh' execution context.  for
        example:

            tmp = sh(_out=StringIO())

        'out' would end up in here as an entry in the baked_args dict"""
        ...

    def __getitem__(self, k):  # -> list[Any] | type[ErrorReturnCode] | type[__class_ErrorReturnCodeMeta] | Any | str:
        ...
    @staticmethod
    def b_which(program, paths=...):  # -> None:
        ...

class Contrib(ModuleType):
    @classmethod
    def __call__(cls, name):  # -> Callable[..., Any]:
        ...

mod_name = ...
contrib = ...

@contrib("git")
def git(orig):
    """most git commands play nicer without a TTY"""
    ...

@contrib("bash")
def bash(orig): ...
@contrib("sudo")
def sudo(orig):
    """a nicer version of sudo that uses getpass to ask for a password, or
    allows the first argument to be a string password"""
    ...

@contrib("ssh")
def ssh(orig):
    """An ssh command for automatic password login"""
    class SessionContent: ...
    class SSHInteract: ...

def run_repl(env):  # -> None:
    ...

class SelfWrapper(ModuleType):
    def __init__(self, self_module, baked_args=...) -> None: ...
    def __getattr__(
        self, name
    ):  # -> list[Any] | type[ErrorReturnCode] | type[__class_ErrorReturnCodeMeta] | Any | str:
        ...
    def bake(self, **kwargs):  # -> Self:
        ...

if __name__ == "__main__":
    env = ...
else: ...
