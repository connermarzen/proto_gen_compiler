# Protogen

* **[Home]()** &larr; you are here
* [Syntax Starter](syntax.md)
* [Understanding The Generated Python](generated/python.md)

---

Welcome! Protogen is a pure-Python implementation of a protocol generator.

## Motive

My inspiration came from [Google Protocol Buffers (Protobuf)](https://developers.google.com/protocol-buffers), and if you have used it before, you will identify clear similarities (particularly in the file syntax). While I really liked Protobuf to start, there were a couple of things that didn't resonate well with me; as such, I tried to roll my own solution. The biggest drivers for me were:

1. **Protobuf's removal of `required` in proto3.** This was largely unappealing to me. There is a lot of back in forth in a variety of communities about the usage of required within protocols, and I am on the pro-required side. For many projects, it entirely makes sense to set required parameters. In my opinion, if something is absolutely necessary for basic program operation, then by all means, it makes sense to reduce packet traffic at the minor expense of local processing. Ultimately, if someone has a strict hatred for required attributes, they need only require their codebase to follow the paradigm that they have set.
2. **Protobuf's use of meta classes instead of actual python classes.** When getting started with Protobuf, I was quite excited to see all the various languages that were supported. The biggest letdown to me is how their Python classes are not generated like the rest of the supported languages. Sure, it still worked, but my IDE did not identify any of the attributes, and it was annoying to bounce back and forth between the protocol, rather to look at the attributes as a code suggestion in my editor.
3. **Protobuf's installation procedure.** I was not attracted to the work that went into installing the Protobuf Compiler and the respective languages. In fact, to install the Python output, one must use `sudo` with Pip, which reeks to me. I wasn't doing any major system operations, so why would I need it? If one could simply install everything with Pip or *some other handy-dandy package manager*, why wouldn't they? Ultimately, the goal for my library was to effective require nothing more than a `pip install` and then to be able to use the compiler as a fully fledged Python module; I did exactly that.

By all means, I think it is a really great solution (Protobuf, that is), but there are also some more optimistic reasons why I chose to roll my own:
1. **I have dreamed of writing my own open source library.** First and foremost, since graduating with my Computer Science degree and working in Software, I have been dying to contribute to open source. I figured that the best way to do that would be to invent something entirely new, but practically speaking, this is a much more feasible approach as a new and growing developer. By working along side things that already exists, I have been able to create my own thing from scratch with a similar conceptual ideal as something that already existed.
2. **I have a desire to understand the compiling process.** I have been interested in the process of code compiling and by writing this, I have been able to get a foundational understand of the it. I used [lark-parser](https://github.com/lark-parser/lark), "a modern parsing library for Python" to perform the parsing, but even still, using that library gave me a really good understanding of the process.

## Features

> Currently `proto_gen_compiler` only compiles code into Python, but I would like to begin supporting more languages. I consider this very much a rough first pass, and intend to continuously improve the code as I go.

### Current Features
* Custom, easy-to-read/write language for generating protocol types.
* Fast, pure-Python implementation
* Parses and generates multiple files at once
* Relatively small, self-contained library
  * Written in a highly object-oriented style for extensibility.

### Future Goals
* Multiprocessing/threading for very large protogen files/projects
* Extended language support for more languages:
  * C/C++
  * C#
  * Java
  * Javascript
  * ... &larr; *your desired language goes here*
* Minification of `.protogen` files for big projects.
  * Also, extension of minified files
* Caching of generated files for faster generation