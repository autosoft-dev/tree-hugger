# tree-hugger
A light-weight, high level, universal code parser built on top of tree-sitter

## System Requirement

- Python 3.6

## Browse the doc

1. [What is it?](#what-is-it)

2. [Why do I need it?](#why-do-i-need-it)

3. [Design Goals](#design-goals)

4. [Installation](#installation)

5. [Building the .so Files](#building-the-so-files)

6. [A Quick Example](#a-quick-example)

7. [One or two words about extending](#one-or-two-words-about-extending)
  
    - [Queries](#queries)

    - [Parser Class](#parser-class)

8. [Roadmap](#roadmap)

-------------



## What is it?

`tree-hugger` is a light weight wrapper around the excellent [`tree-sitter`](https://github.com/tree-sitter/tree-sitter) library and it's Python binding. You can use it to create your universal code parser and then easily mine through the data. 

## Why do I need it?

`tree-sitter` is a great universal code parser and does it's job without any problem and very very fast. But it is also pretty low-level. The Python binding makes you work with ugly looking `sexp` to run a query and get the result. It also does not support the NodeVisitor kind of features that are available in Python's native `ast` module.

At [CodistAI](https://codist-ai.com) we have been using `tree-sitter` for some time now to create a language independent layer for our code analysis and code intelligence platform. While bulding that, we faced the pain as well. And we wrote some code to easily extend our platform to different languages. We believe some others may as well need to have the same higher level library to easily parse and gain insight about various different code files.

## Design Goals

- Light-weight
- Extendable
- Provides easy higher-level abstrctions
- Normalization across languages (Coming soon!)

## Installation

### From pip:

Just do
```
pip install tree-hugger
```

### From Source:

```
git clone https://github.com/autosoft-dev/tree-hugger.git

cd tree-hugger

pip install -e .
```

_The installation process is tested in macOS Mojave, we have a [separate docker binding](https://github.com/autosoft-dev/tree-sitter-docker) for compiling the libraries for Linux and soon this library will be integrated in that as well_

_You may need to install libgit2. In case you are in mac just use `brew install libgit2`_

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
And once copied, we place it under a directory called `tslibs` (It is in the .gitignore). But of course, if you are using linux then this command probably won't work and you will need to use our [tree-sitter-docker](https://github.com/autosoft-dev/tree-sitter-docker) image and manually copy the final .so file.

Another thing that we need before we can analyze any code file is an yaml with queries. We have suuplied one example query file
under [**queries**](https://raw.githubusercontent.com/autosoft-dev/tree-hugger/master/queries/example_queries.yml) directory. 

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
pp.get_all_function_documentation()
Out[5]:
{'parent': '"""This is the parent function\n    \n    There are other lines in the doc string\n    This is the third line\n\n    And this is the fourth\n    """',
 'first_child': "'''\n        This is first child\n        '''",
 'second_child': '"""\n        This is second child\n        """',
 'my_decorator': '"""\n    Outer decorator function\n    """',
 'say_whee': '"""\n    Hellooooooooo\n\n    This is a function with decorators\n    """'}
 ```

 *(Notice that, in the last call, it only returns the functions which has a documentation comment)*


## One or two words about extending

Extending tree-hugger for other languages and/or more functionalities for the already provided ones, is easy. 

You need to understand that there are two main things here.

1. ### Queries: 
Queries are s-expressions (Remember LISP?) that works on the parsed code and gives you what you want. They are a great way to fetch arbitary data from the parsed code without having to travel through it recursively. 
Tree-hugger gives you a way to write your queries in yaml file (Check out the [queries/example_queries.yml](queries/example_queries.yml)) file to see some examples. 

This file has a very simple structure. Each main section is named `<language>_queries` where `language` is the name of the language that you are writing queries on. In the case of the example file, it is `python`. 

This main section  is further sub-divded into few (as many as you need, actually) sections. Each of them has the same structure. A name of a query followed by the query itself. Written as an s-expression. One example:

```
all_function_docstrings:
        "
        (
            function_definition
            name: (identifier) @function.def
            body: (block(expression_statement(string))) @function.docstring
        )
        "
```
Of course, you have to follow yaml grammar while writing these queries. You can see a bit more about writng these queries in the documentation of tree-sitter. [Here](https://tree-sitter.github.io/tree-sitter/using-parsers#pattern-matching-with-queries). Although it is not very intuitive to start with. We are planning to write a detailed tutorial on this subject. 

Some example queries, that you will find in the yaml file (and their corresponding API from the PythonParser class) - 

```
* all_function_names => get_all_function_names()

* all_function_docstrings => get_all_function_documentation()

* all_class_methods => get_all_class_method_names()
```

2. ### Parser Class:
A parser class (such as PythonParser) extends from the BaseParser class. The only mandatory argument that a Parser class should pass to the parent is the `language`. This is a string. Such as `python` (remember, lower case). Although, each parser class must
have the options to take in the path of the tree-sitter library (.so file that we are using to parse the code) and the path to the queries yaml file, in their constructor. As an example, for PythonParser - 

```
from tree_hugger.core.code_parser import BaseParser, match_from_span


class PythonParser(BaseParser):
  def __init__(self, library_loc: str=None, query_file_path: str=None):
    super(PythonParser, self).__init__('python', 'python_quaries', library_loc, query_file_path)
```

As you can see, the BaseParser class needs a third (mandatory) argument, the name of the language. Each Parser class has the responsibility to pass that to the BaseParser class (as hard-coded string for the moment)

The BaseParser class can do few things for you. 

* It loads and prepares the .so file with respect to the language you just mentioned. 

* It loads, parses, and prepares the query yaml file. (for the queries, we internally use an extended UserDict class. More on that later.)

* It gives an API to parse a file and prepare it for query. `BaseParser.parse_file`

* It also gives you another (most likely not to be exposed outside) API `_run_query_and_get_captures` which lets you run any queries and return back the matched results (if any) from the parsed tree. 

If you are interested to see the example of one of the methods in the PythonParser class, to know how all of these come toghether. Here it is (Do not forget, we use those APIs once we have called `parse_file` and parsed the file) - 

```
def get_all_function_names(self) -> List:
        """
        Gets all function names from a file.

        It excludes all the methods, i.e. functions defined inside a class
        """

        # First let us run the query. Mention the name of the query from yaml file and also pass in the root_node
        # The root_node is already prepared for you once you had called the parse_file method beforehand
        captures = self._run_query_and_get_captures('all_function_names', self.root_node)

        # Now, with the returned captures, let's get the string representations using `match_from`span` 
        all_funcs = set([match_from_span(n[0], self.splitted_code) for n in captures])

        # This part here, uses another method from PythonParser class to get the name of all the class methods. 
        methods = self.get_all_class_method_names()
        all_methods = set([method_name  for key, value in methods.items() for method_name in value])

        # Let's return the difference between the two sets.
        return list(all_funcs - all_methods)
```

The function `match_from_span` is a very handy function. It is defined in the BaseParser module. It takes a span definition and returns the underlying code string from it.

## Roadmap

 * Finish PythonParser

 * ~~Create pypi packages and make it installable via pip~~

 * Write more documentation

 * Write *Parser class for other languages

| Languages        | Status-Finished           | Author  |
| ------------- |:-------------:| -----:|
| Python     | 40% | [Shubhadeep](https://github.com/rcshubhadeep) |
| PHP      | 0%      |   NULL |
| Java | 0%      |    NULL |
| JavaScript | 0%      | NULL | 
