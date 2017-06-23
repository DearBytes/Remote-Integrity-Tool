# Contributing
So you want to contribute to this project? Awesome! This document should help you get started.

## Code style
Most important of all, code style. When writing any Python code, please use the [default Python code standard (PEP 8)](https://www.python.org/dev/peps/pep-0008/).
This should mostly get you started, but here's some project specific things to stick to:

* Every public method should be documented with a reStructuredText docstring that 
  can be read by PyCharm, full specs can be found on the [JetBrains website](https://www.jetbrains.com/help/pycharm/using-docstrings-to-specify-types.html)
  but just looking through the code should give you an idea of how to do it.
  
* Give your variables and methods **descriptive names**, nobody likes reading `p() + q() * a`,
  name them so other people know what you mean (this also includes private methods!). Example:
  `pointer() + query_index() * amount`, much better right? This isn't required in comprehension statements,
  however it is recommended if it doesn't make your statement too long. Example: `cores = list(a.core for a in apples)`.
  
* Try keeping your methods short, if they get any longer than 20 lines of code, break them up into one public method
  which calls multiple private sub-methods.
