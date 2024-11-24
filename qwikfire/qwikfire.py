# trunk-ignore-all(ruff/PGH003,ruff/F821)
import logging
import re
from functools import wraps
from shlex import split
from typing import Any, Callable, Concatenate, Final, Optional, ParamSpec, TypeVar

from sh import Command, CommandNotFound, RunningCommand

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

VARS_RE = re.compile("\\{\\{\\s*(\\w+)\\s*\\}\\}")
"""Regex pattern for Jinja style variable substitution blocks"""


class QuickFireException(Exception):
  """The root class of the exception hierarchy.

  Users can use this exception directly with @quickfire annotations. Best to subclass it
  with specific meaning for the package or application quickfire is being used on.

  Args:
      Exception (_type_): create domain specific exceptions extending this class
  """
  def __init__(self, message: str, e: Exception, annotated_instance: Any):
    """Creates a new QuickFireException wrapper exception. Used directly in annotations
    or subclassed for package and application specific exceptions.

    Args:
        message (str): a message to describe the exception
        e (Exception): the underlying shell related exception: see [sh exceptions](https://sh.readthedocs.io/en/latest/sections/command_class.html#exceptions)
        annotated_instance (Any): the instance of the annotated class
    """
    self._exception: Final[Exception] = e
    self._annotated_instance = annotated_instance
    super().__init__(message)

  @property
  def exception(self) -> Exception:
    """Gets the underlying shell exception wrapped by this exception

    Returns:
        Exception: the underlying sh exception: see [sh exceptions](https://sh.readthedocs.io/en/latest/sections/command_class.html#exceptions)
    """
    return self._exception

  @property
  def annotated_instance(self) -> Any:
    """Gets the instance of the annotated class.

    Returns:
        Any: instance of the class annotated with the @quickfire decorator annotation
    """
    return self._annotated_instance

  @property
  def result(self) -> Any:
    """Gets the QuickFireResults object.

    TODO: Due to an ordering problem in this file (and the dependency between
    QuickFireException and QuickFireResults) the result property uses Any.

    Returns:
        Any: the QuickFireResults with or without the command producing this exception
    """
    return self._result

  @result.setter
  def result(self, result: Any) -> None:
    """Sets the QuickFireResult object collected before this exception was raised."""
    self._result = result

"""Callable return Generic Type"""
_T = TypeVar('_T')
"""Callable parameter specification"""
_P = ParamSpec('_P')
"""Alias for generalized Callable"""
GFunc = Callable[...,Any]

def quickfire(e: type[QuickFireException], *command: str) -> GFunc:
  """Decorator factory function to capture arguments"""
  def decorator(function: Callable[Concatenate[Any,QuickFire,_P], _T]) -> GFunc:
    """Decorator function itself"""
    @wraps(function)
    def wrapper(self: Any, *args: _P.args, **kwargs: _P.kwargs) -> _T:
      """The wrapper function calling target"""
      qf = QuickFire(function, e, *command)
      return function(self, qf, *args, **kwargs)
    return wrapper
  return decorator

def _substitute(var_key: str, var_val: str, command: str) -> str:
  # Performs a single Jinja like substitution
  pat = "\\{\\{\\s*" + var_key + "\\s*\\}\\}"
  regex = re.compile(pat)
  return regex.sub(str(var_val), command)

def _substitute_all(command: str, **kwargs: Any) -> str:
  #Performs substitutions looping on all commands
  substituted: str = command
  for sub_key in kwargs:
    sub_value = kwargs[sub_key]
    substituted = _substitute(sub_key, sub_value, substituted)
  return substituted


class QuickFireResult:
  """The run results of both single and multiple commands in an @quickfire annotation
  """
  def __init__(self, annotated_instance: Any, commands :RunningCommand):
    """Creates an instance of QuickFireResult with its first mandatory command

    Args:
        annotated_instance (Any): the instance of the class whose methods are annotated
        commands (RunningCommand): the commands in the annotation
    """
    self._annotated_instance: Final[Any] = annotated_instance
    self._results: Final[list[RunningCommand]] = []
    self._results.append(commands)

  def append(self, command: RunningCommand):
    """Append RunningCommands, used by annotations with more than one command

    Args:
        command (RunningCommand): an executed command's results
    """
    self._results.append(command)

  def result(self, index: Optional[int] = None) -> RunningCommand:
    """Gets the first or only command result, RunningCommand, at index 0 or at a specific index

    Args:
        index (Optional[int], optional): the optional index or 0 is used

    Returns:
        RunningCommand: the command at the index
    """
    if index is None:
      return self._results[0]
    else:
      return self._results[index] # type: ignore

  def concat_stdout(self) -> bytes:
    """Concatenates all command output to stdout into a single buffer

    Returns:
        bytes: a single buffer with every command's stdout appended
    """
    if len(self._results) == 1:
      return self._results[0].stdout  # type: ignore
    output: bytes = b''
    for r in self._results:
      output += r.stdout  # type: ignore
    return output  # type: ignore

  def concat_stderr(self) -> bytes:
    """Concatenates all command error output to stderr into a single buffer

    Returns:
        bytes: a single buffer with every command's stderr appended
    """
    if len(self._results) == 1:
      return self._results[0].stderr # type: ignore
    output: bytes = b''
    for r in self._results:
      output += r.stderr  # type: ignore
    return output  # type: ignore

  @property
  def results(self) -> list[RunningCommand]:
    """Gets the list of all results

    Returns:
        list[RunningCommand]: all the results as an ordered list
    """
    return self._results

  @property
  def annotated_instance(self) -> Any:
    """Gets the instance of the annotated class

    Returns:
        Any: could be any user defined class
    """
    return self._annotated_instance

  @property
  def exit_code(self, index: Optional[int] = 0) -> int:
    """Gets the exit_code of the first/only RunningCommand result or at a specific index

    Args:
        index (Optional[int], optional): specific index to lookup the command's exit code

    Returns:
        int: the exit code of the command
    """
    return self._results[index].exit_code # type: ignore

  @property
  def exit_codes(self) -> int:
    """Add all exit codes into one value (analogous to concat_std[out|err])

    Returns:
        int: the sum of all command result exit codes
    """
    if len(self._results) == 1:
      return self._results[0].exit_code # type: ignore
    output: int = 0
    for r in self._results:
      output += r.exit_code # type: ignore
    return output # type: ignore

  @property
  def stripped(self, encoding: Optional[str] = 'UTF-8') -> str:
    """Gets the decoded concatenated standard output with right and left whitespace stripped

    Usually this is all that's ever needed to process the output if at all.

    Args:
        encoding (Optional[str], optional): use 'UTF-8' encoding by default

    Returns:
        str: the decoded concatenated standard output with right and left whitespace stripped
    """
    return self.concat_stdout().decode(encoding).rstrip().lstrip() # type: ignore

  @property
  def stdout(self, encoding: Optional[str] = 'UTF-8') -> str:
    """Gets the decoded concatenated standard output

    Args:
        encoding (Optional[str], optional): use 'UTF-8' encoding by default

    Returns:
        str: the decoded concatenated standard output
    """
    return self.concat_stdout().decode(encoding) # type: ignore

  @property
  def stderr(self, encoding: Optional[str] = 'UTF-8') -> str:
    """Gets the decoded concatenated standard error output

    Args:
        encoding (Optional[str], optional): use 'UTF-8' encoding by default

    Returns:
        str: the decoded concatenated standard error output
    """
    return self.concat_stderr().decode(encoding) # type: ignore


class QuickFire:
  """Rapidly fires off short lived, synchronous, blocking, sequential shell commands in
  a working directory with exception handling, and logging.
  """

  def __init__(self, function: GFunc, e: type[QuickFireException], *commands: str):
    """Creates a new instance of QuickFire within the decorator for the annotated method

    Args:
        function (Callable[_P, _T]): the annotated decorated function
        e (type[QuickFireException]): the wrapper exception type
        *commands (str): the string array of commands to execute
    """
    self._exception: Final[type[QuickFireException]] = e
    LOG.debug(f"__init__():  re-raised exception = {e.__name__}")
    self._commands = commands
    LOG.debug(f"__init__():  annotation commands = {commands}")
    self._function = function
    LOG.debug(f"__init__():  annotated function  = {function.__qualname__}")

  @property
  def function(self) -> GFunc:
    return self._function

  @property
  def raises(self) -> type[QuickFireException]:
    """Gets the wrapper exception class raised

    Returns:
        type[QuickFireException]: either QuickFireException or a subclass
    """
    return self._exception

  def _run(self, cmd: str, qfr: QuickFireResult|None, annotated_instance: Any, **kwargs: Any) -> QuickFireResult:
    # extract _xxxx kwargs intended for pass through to sh.Command
    sh_args: dict[str,Any] = {}
    for arg in kwargs:
      if arg.startswith('_'):
        sh_args[arg] = kwargs[arg]
        LOG.debug(f"passing through '{arg}'='{kwargs[arg]}' to sh")
    # injected to override so return codes are accessible when not 0
    sh_args['_return_cmd']=True

    # perform substitutions using kwargs key value pairs on the command
    LOG.debug(f"Running command '{cmd}' for {annotated_instance} with kwargs = {kwargs}")
    substituted = _substitute_all(cmd, **kwargs)
    cmd_args = split(substituted)
    LOG.info(f"split substituted command = {cmd_args}")

    # prepare sh.Command, raises CommandNotFound exception if which command fails
    try:
      sh_cmd = Command(cmd_args[0])
    except CommandNotFound as raised:
      LOG.exception(f"CommandNotFound exception raised when building the command: '{cmd_args[0]}'")
      wrapper_exception = self._exception.__new__(self._exception)
      wrapper_exception.__init__(f"Failed executing command '{cmd}'",
          raised, annotated_instance)
      wrapper_exception.result = qfr # for the sake of earlier run commands
      raise wrapper_exception from raised

    # run the command providing additional arguments
    try:
      result: RunningCommand = sh_cmd(cmd_args[1:], **sh_args) # type: ignore
    except Exception as raised:
      LOG.exception(f"Exception raised when trying to run the command: '{cmd}'")
      wrapper_exception = self._exception.__new__(self._exception)
      wrapper_exception.__init__(f"Failed executing command '{cmd}'",
          raised, annotated_instance)
      wrapper_exception.result = qfr # for the sake of earlier run commands
      raise wrapper_exception from raised

    # create a QFR inst if not already created and append each command's results
    if qfr is None:
      qfr = QuickFireResult(annotated_instance, result) # type: ignore
    else:
      qfr.append(result) # type: ignore
    return qfr

  def run(self, annotated_instance: Any, **kwargs: Any) -> QuickFireResult:
    """Runs one or more commands in the @quickfire method annotation

    Args:
        annotated_instance (Any): the instance of the annotated user defined class

    Returns:
        QuickFireResult: the result of running the command[s]
    """
    # use sh_defaults if provided by the annotated user defined class
    sh_defaults = getattr(annotated_instance, "sh_defaults", None)
    if callable(sh_defaults):
      defaults = annotated_instance.sh_defaults() # type: ignore
      LOG.info(f"Using shell and variable defaults from {self}: '{defaults}'")
      for arg in defaults:
        if not kwargs.get(arg):
          LOG.info(f"Adding shell and variable default key '{arg}' with value '{defaults[arg]}'")
          kwargs[arg]=defaults[arg]
        else:
          LOG.info(f"Not overriding '{arg}' with value '{defaults[arg]}': keeping value '{kwargs[arg]}'")
    else:
      LOG.debug(f"No sh_defaults() method detected on {self}")

    # cycle and run each command one after the other
    qfr = self._run(self._commands[0], None, annotated_instance, **kwargs)
    for ii in range(1, len(self._commands)):
      cmd = self._commands[ii]
      qfr = self._run(cmd, qfr, annotated_instance, **kwargs)
    return qfr
