"""@quickfire annotations decorate class methods with shell commands

QuickFire is a simple decorator used to annotate class methods with shell commands. It
injects an extra, hidden, QuickFire argument, into a method's argument list right after
`self`. The method implementation can use the `qf` handle to execute the shell commands
listed in the annotation using a one-liner: `qf.run()`.

QuickFire and its annotation is properly typed preventing Python typing tools (i.e pyright,
pyre, mypy) from needlessly littering your code with complaint's. This is a common problem
with decorators that inject additional parameters: the signature of the definition differs
from the signature of the called method.

Why?:
  Even with the glorious [sh package](https://sh.readthedocs.io/en/latest/), I still find
  myself writing boilerplate code, logging, error handling and raising higher level
  (wrapper) exceptions specific to the nature of the package or application using sh. Even
  though sh does a great job minimizing the boilerplate, it still clutters my code, and
  reduces its readability. Other code maintainers will still need to know about `sh` and
  how I used it.

QuickFire's annotation concisely and neatly documents what the method does while also
removing repetitive boilerplate for setup, logging, and error handling: essentially
most system shell command overheads. The `@quickfire` annotation also references the
application specific wrapper exception to use when wrapping and re-raising exceptions.
Overall the code is much more readable while the pattern results in pythonic OO code
when chaining command outputs to inputs.

Example:
  Executes two echo commands one after the other using Jinja style variable substitution.
  If an exception were to occur it would be wrapped with the user defined WrappingException
  which extends QuickFireException::

    class WrappingException(QuickFireException):
    ...
    @quickfire(WrappingException, "echo {{hello_var}}", "echo {{world_var}}")
    def many_twovars(self, qf: QuickFire) -> str:
      return qf.run(self, hello_var="hello", world_var="world").stripped

    ...
    instance.many_twovars()

  Callers do not include the injected hidden QuickFire argument intended for the
  implementation to use. Notice no warnings arise when callers invoke the example method
  above with `instance.many_twovars()`.

As seen from the example above, try except blocks, conditional checks, logging, etc most
of the boilerplate is gone. Reading and understanding what the method does and what exception
it raises makes the pattern self documenting.

sh package kwargs (see https://sh.readthedocs.io/en/latest/sections/special_arguments.html#)
can be used in the run() method. They're prefixed with `_`, and are passed through to the
`sh.Command`. If the class whose methods are annotated, exposes a dictionary accessor method
called `sh_defaults()`, the values of the dictionary it returns are used for defaults both
for variable substitutions and for pass through arguments to the `sh.Command`. Method
specific kwarg key pairs provided to the run method override these defaults.

NOTE: Piped commands do **NOT** work. Use output chaining of one annotated method as
input into another, if needed as a one off. Multiple semi-colon separated commands in the
same string, i.e. "echo {{hello_var}}; echo {{world_var}}" will **NOT** work, just use
separate commands in the variadic string commands array.

If you find you need these or other shell features you're probably over doing it. Write an
actual shell script and execute that instead, or directly use the `sh package` in your code.
QuickFire is purposefully meant to be trivial and there for the occasional shell command
without having to clutter up your code.
"""
