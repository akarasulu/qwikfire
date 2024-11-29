"""@qwikfire annotations decorate class methods with one or more shell commands

QwikFire is a decorator. Use it to annotate class methods with a list of shell commands.
The decorator injects an extra (hidden) QwikFire argument into a method's argument list
right after `self`. The implementation uses the `qf` handle to execute all listed shell
commands in the annotation using a one-liner: `qf.run()`.

Example:
  Executes two echo commands one after the other using Jinja style variable substitution.
  If an exception were to occur it will be caught, wrapped within a user defined, domain
  specific WrappingException which extends QwikFireException, and re-raised::

    class WrappingException(QwikFireException):
    ...
    @qwikfire(WrappingException, "echo {{hello_var}}", "echo {{world_var}}")
    def many_twovars(self, qf: QwikFire) -> str:
      return qf.run(self, hello_var="hello", world_var="world").stripped

    ...
    # invoking the method without the (hidden) QwikFire argument
    instance.many_twovars()

  Callers do not include the injected hidden QwikFire argument intended for the
  implementation to use. Notice that no warnings arise with callers missing the
  QwikFire argument: i.e. `instance.many_twovars()`.

The example above, demonstrates how almost all the boilerplate for try / except blocks,
conditional checks, logging, etc, is gone. Reading and understanding what commands the
method executes and what exceptions it raises makes the annotation self documenting.

QwikFire and its annotation is properly typed preventing Python typing tools (i.e pyright,
pyre, mypy) from needlessly littering your code with complaint's. This is a common problem
with decorators that inject additional parameters since the signature of the definition
differs from the signature of callers. Overall the code is much more readable while the
pattern results in pythonic OO code when chaining method outputs to other method inputs.

sh package kwargs (see https://sh.readthedocs.io/en/latest/sections/special_arguments.html#)
can be used in the run() method. They're prefixed with `_`, and are passed through to the
`sh.Command`. If the class whose methods are annotated, exposes a dictionary accessor method
called `sh_defaults(self, method: Caller[..., Any])`, the values of the dictionary it returns
are used for defaults both for variable substitutions and for pass-through arguments to the
`sh.Command`. NOTE: the method is provided to, if needed, tailor defaults to specific class
methods. Method specific kwarg key pairs provided to the run method override these defaults.

Why?:
  Even with the glorious [sh package](https://sh.readthedocs.io/en/latest/), I still
  find myself writing boilerplate code, logging, error handling and raising higher level
  (wrapper) exceptions specific to the domain of the package or application using sh. Even
  though sh does a great job minimizing the boilerplate, it still clutters my code, and
  reduces its readability. Other code maintainers will still need to know about `sh` and
  how I used it.

NOTE: Piped commands do **NOT** work. Use output chaining of one annotated method as
input into another, if needed as a one off. Multiple semi-colon separated commands in the
same string, i.e. "echo {{hello_var}}; echo {{world_var}}" will **NOT** work, just use
separate commands in the variadic string commands array.

If you find you need these or other shell features you're probably over doing it. Write an
actual shell script and execute that instead, or directly use the `sh package` in your code.
QwikFire is purposefully meant to be simple and there to prevent the occasional shell command
from cluttering up your code.
"""
