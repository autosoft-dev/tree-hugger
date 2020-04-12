# tree-hugger
A light-weight, high level, universal code parser built on top of tree-sitter

## Browse the doc

1. [What is it?](#what-is-it)

2. [Why do I need it?](#why-do-i-need-it)

3. [Design Goals](#design-goals)

4. [Installation](#installation)

5. [Building the .so Files](#building-the-so-files)

6. [A Quick Example](#a-quick-example)

7. [Roadmap](#roadmap)

-------------



## What is it?

`tree-hugger` is a light weight wrapper around the excellent [`tree-sitter`](https://github.com/tree-sitter/tree-sitter) library and it's Python binding. 

## Why do I need it?

`tree-sitter` is a great library and does it's job without any problem and very very fast. But it is also pretty low-level. The Python binding makes you work with ugly looking `sexp` to run a query and get the result. It also does not support the NodeVisitor kind of features that are available in Python's native `ast` module.

At [CodistAI](https://codist-ai.com) we have been using `tree-sitter` for some time now to create a language independent layer for our code analysis and code intelligence platform. While bulding that, we faced the pain as well. And we wrote some code to easily extend our platform to different languages. We believe some others may as well need to have the same higher level library to easily parse and gain insight about various different code files.

## Design Goals

- Light-weight
- Extendable
- Provides easy higher-level abstrctions
- (Should)Offer some kind of normalization across languages

## Installation

At the moment a `pip` wheel is not available (coming soon!) so the best way to install it is to clone the library and then run the following commands (from the top level directory)

_The installation process is tested in macOS Mojave, we have a [separate docker binding](https://github.com/autosoft-dev/tree-sitter-docker) for compiling the libraries for Linux and soon this library will be integrated in that as well_

- First install libgit2 `brew install libgit2`
- Install all the requirements for the library `pip install -r requirements.txt`
- Install the library `pip install .`

## Building the .so files

_Please note that building the libraries has been tested under a macOS Mojave with Apple LLVM version 10.0.1 (clang-1001.0.46.4)_

_Please check out our Linux specific instructions [here](https://github.com/autosoft-dev/tree-sitter-docker)_

Once this library is installed it gives you a command line utility to download and compile tree-sitter .so files with ease. As an example - 

```
create_libs python
```

Here is the full usage guide of the command

```
usage: create_libs [-h] [-c] [-l LIB_NAME] langs [langs ...]

positional arguments:
  langs                 Give the name of languages for tree-sitter (php,
                        python, go ...)

optional arguments:
  -h, --help            show this help message and exit
  -c, --copy-to-workspace
                        Shall we copy the created libs to the present dir?
                        (default: False)
  -l LIB_NAME, --lib-name LIB_NAME
                        The name of the generated .so file
```

## A Quick Example

First run the above command to generate the libraries. 

In our settings we just use the `-c` flag to copy the generated `tree-sitter` library's `.so` file to our workspace.
And once copied, we place it under a directory called `tslibs` (It is in the .gitignore).

Another thing that we need before we can analyze any code file is an yaml with queries. We have suuplied one example query file
under `queries` directory. 

*Please note that, you can set up two environment variables `QUERY_FILE_PATH` and `TS_LIB_PATH` for the query file path and 
tree-sitter lib path and then the libary will use them automatically. Otherwise, as an alternative, you can pass it when creating any `*Parser` object*

Assuming that you have the necessary environment variable setup. The following line of code will create a `PythonParser` object

```python
from tree_hugger.core import PythonParser

pp = PythonParser()
```

And then you can pass in any Python file that you want to analyze, like so :

```python
pp.parse_file("tests/assets/file_with_different_functions.py")
Out[3]: True
```

`parse_file` returns `True` if success

And then you are free to use the methods exposed by that particular Parser object. As an example - 

```python
pp.get_all_function_names()
Out[4]:
['first_child',
 'second_child',
 'say_whee',
 'wrapper',
 'my_decorator',
 'parent']
```

OR

```python
pp.get_all_function_docstrings()
Out[5]:
{'parent': '"""This is the parent function\n    \n    There are other lines in the doc string\n    This is the third line\n\n    And this is the fourth\n    """',
 'first_child': "'''\n        This is first child\n        '''",
 'second_child': '"""\n        This is second child\n        """',
 'my_decorator': '"""\n    Outer decorator function\n    """',
 'say_whee': '"""\n    Hellooooooooo\n\n    This is a function with decorators\n    """'}
 ```

 *(Notice that, in the last call, it only returns the functions which has a docstring)*


 ## Roadmap

 * Finish PythonParser

 * Create pypi packages and make it installable via pip

 * Write more documentation

 * Start other languages

 |  Languages  |  Finsihed  |
 |__________________|____________|
 |   Python    |     20%    |
 |   PHP       |     0%     |
 |   Java      |     0%     |
 |   JavaScript|     0%     |
 |   C++       |     0%     |