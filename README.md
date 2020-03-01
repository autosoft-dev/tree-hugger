# tree-hugger
A light-weight, high level, universal code parser built on top of tree-sitter

## Browse the doc

[What is it?](#what-is-it)

[Why do I need it?](#why-do-i-need-it)

[Design Goals](#design-goals)

[Installation](#installation)

[Building the .so Files](#building-the-so-files)

-------------



## What is it

`tree-hugger` is a light weight wrapper around the excellent [`tree-sitter`](https://github.com/tree-sitter/tree-sitter) library and it's Python binding. 

## Why do I need it

`tree-sitter` is a great library and does it's job without any problem and very very fast. But it is also pretty low-level. The Python binding makes you work with ugly looking `sexp` to run a query and get the result. It also does not support the NodeVisitor kind of features that are available in Python's native `ast` module.

At [CodistAI](https://codist-ai.com) we have been using `tree-sitter` for some time now to create a language independent layer for our code analysis and code intelligence platform. While bulding that, we faced the pain as well. And we wrote some code to easily extend our platform to different languages. We believe some others may as well need to have the same higher level library to easily parse and gain insight about various different code files.

## Design Goals

- Light-weight
- Extendable
- Provides easy higher-level abstrctions
- Offers some kind of normalization across languages

## Installation

At the moment a `pip` wheel is not available (coming soon!) so the best way to install it is to clone the library and then run the following commands (from the top level directory)

_The installation process is tested in macOS Mojave, we have a [separate docker binding](https://github.com/autosoft-dev/tree-sitter-docker) for compiling the libraries for Linux and soon this library will be integrated in that as well_

- First install libgit2 `brew install libgit2`
- Install all the requirements for the library `pip install -r requirements.txt`
- Install the library `pip install .`

## Building the so files

_Please note that building the libraries has been tested under a macOS Mojave with Apple LLVM version 10.0.1 (clang-1001.0.46.4)_

_Please check out our Linux specific instructions [here](https://github.com/autosoft-dev/tree-sitter-docker)_

Once this library is installed it gives you a command line utility to download and compile tree-sitter .so files with ease. As an example - 

```
create_libs php python
```

This command gives two options, first the choice to whether it should copy the generated lib to the prsent dir and also gives you a way to mention the name of the target .so file. Please try `create_libs -h` to check all the options.