# trunk-ignore-all(bandit/B101,ruff/PGH003)
import logging
from types import NoneType
from typing import Any

import pytest
import sh

from qwikfire.qwikfire import QwikFire, QwikFireException, QwikFireResult, qwikfire

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)

class WrappingException(QwikFireException):
  def __init__(self, message: str, e: Exception, annotated_instance: Any):
    super().__init__(message, e, annotated_instance)

# logic accounting for pydevd (vscode debugger) messages inserted into stderr
def check_stderr(result: QwikFireResult, expecting_data: bool):
  if expecting_data and result.stderr:
    # we're expecting valid data and there is data in stderr
    return "pydevd: Sending message" not in result.stderr
  else:
    return not expecting_data

class AnnotatedTestClassNoShDefaults:
  @qwikfire(WrappingException, "echo fubar")
  def single_novars(self, qf: QwikFire) -> str:
    LOG.debug(f"got QwikFire instance: {qf}")
    proc: QwikFireResult = qf.run(self, _env={})
    assert proc.result() == proc.result(0)
    assert check_stderr(proc, False)
    assert qf.function.__name__ == 'single_novars'
    assert proc.exit_codes == 0
    assert qf.raises == WrappingException
    return proc.stripped

class AnnotatedTestClass:
  def sh_defaults(self) -> dict[str,Any]:
    defaults: dict[str,Any] = {}
    defaults["test_var"]='one more time'
    defaults['hello_var']="oh no"
    defaults['new_var']="add me in"
    return defaults

  @qwikfire(WrappingException, "eko fubar")
  def raise_exception(self, qf: QwikFire) -> str:
    LOG.debug(f"got QwikFire instance: {qf}")
    try:
      proc: QwikFireResult = qf.run(self, _env={})
    except WrappingException as we:
      LOG.exception("Exception caught")
      assert we.exception.__class__ == sh.CommandNotFound
      assert we.annotated_instance == self
      raise we from None
    return proc.stripped

  @qwikfire(WrappingException, "echo fubar")
  def single_novars(self, qf: QwikFire) -> str:
    LOG.debug(f"got QwikFire instance: {qf}")
    proc: QwikFireResult = qf.run(self, _env={})
    assert proc.result() == proc.result(0)
    assert check_stderr(proc, False)
    assert proc.exit_codes == 0
    assert qf.raises == WrappingException
    return proc.stripped

  @qwikfire(WrappingException, "echo {{test_var}}")
  def single_onevar(self, qf: QwikFire) -> str:
    return qf.run(self).stripped # value comes from sh_defaults

  @qwikfire(WrappingException, "echo {{test_var  }}")
  def single_onevar1(self, qf: QwikFire) -> str:
    return qf.run(self, test_var="not again 1").stripped

  @qwikfire(WrappingException, "echo {{  test_var}}")
  def single_onevar2(self, qf: QwikFire) -> str:
    return qf.run(self, test_var="not again 2").stripped

  @qwikfire(WrappingException, "echo {{   test_var   }}")
  def single_onevar3(self, qf: QwikFire) -> str:
    return qf.run(self, test_var="not  again   3 ").stripped

  @qwikfire(WrappingException, 'echo "{{   test_var   }}"')
  def single_onevar4(self, qf: QwikFire) -> str:
    return qf.run(self, test_var=" not  again   4 ").stripped

  @qwikfire(WrappingException, 'echo "{{   test_var   }}"')
  def single_onevar5(self, qf: QwikFire) -> str:
    result = qf.run(self, test_var=" not  again   5 ")
    assert result.stripped != result.stdout
    # without the lstrip() and rstrip()
    return result.stdout

  @qwikfire(WrappingException, "echo {{fee}} {{fii}} {{foe}} {{fum}}")
  def single_manyvars(self, qf: QwikFire) -> str:
    result = qf.run(self, fee="I smell the blood of ", fii=5,
      foe="Englishmen,", fum="yummy!")
    assert result.concat_stderr() == b''
    return result.stripped

  @qwikfire(WrappingException, "echo hello", "echo world")
  def many_novars(self, qf: QwikFire) -> str:
    return qf.run(self).stripped

  @qwikfire(WrappingException, "echo {{hello_var}}", "echo {{world_var}}")
  def many_twovar(self, qf: QwikFire) -> str:
    result = qf.run(self, hello_var="hello", world_var="world")
    assert not result.concat_stderr()
    assert len(result.results) == 2 # type: ignore
    assert result.annotated_instance == self
    assert result.exit_code == 0
    assert result.exit_codes == 0
    assert len(result.stderr) == 0
    return result.stripped

  @qwikfire(WrappingException, "true", "false")
  def many_novar_fail(self, qf: QwikFire) -> None:
    qf.run(self, hello_var="hello", world_var="world")

def test_single_novars():
  assert AnnotatedTestClass().single_novars() == "fubar"

def test_single_novars_no_sh_defaults():
  assert AnnotatedTestClassNoShDefaults().single_novars() == "fubar"

def test_single_onevar():
  assert AnnotatedTestClass().single_onevar() == "one more time"
  assert AnnotatedTestClass().single_onevar1() == "not again 1"
  assert AnnotatedTestClass().single_onevar2() == "not again 2"
  assert AnnotatedTestClass().single_onevar3() == "not again 3"
  assert AnnotatedTestClass().single_onevar4() == "not  again   4"
  assert AnnotatedTestClass().single_onevar5() == " not  again   5 \n"

def test_single_manyvars():
  assert AnnotatedTestClass().single_manyvars() == "I smell the blood of 5 Englishmen, yummy!"  # type: ignore

def test_many_novars():
  assert AnnotatedTestClass().many_novars() == "hello\nworld"

def test_many_twovar():
  assert AnnotatedTestClass().many_twovar() == "hello\nworld"

def test_exception():
  with pytest.raises(WrappingException) as excinfo:
    tc = AnnotatedTestClass()
    tc.raise_exception()
  LOG.error(f"excinfo caught = {excinfo}")
  assert isinstance(excinfo.value, WrappingException)
  assert excinfo.value.result.__class__ is QwikFireResult or NoneType
  assert str(excinfo.value) == "Failed executing command 'eko fubar'"

def test_many_novar_fail():
  with pytest.raises(WrappingException) as excinfo:
    tc = AnnotatedTestClass()
    tc.many_novar_fail()
  LOG.error(f"excinfo caught = {excinfo}")
  assert isinstance(excinfo.value, WrappingException)
  assert excinfo.value.result.__class__ is QwikFireResult or NoneType
  assert str(excinfo.value) == "Failed executing command 'false'"
