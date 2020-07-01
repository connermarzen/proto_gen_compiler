import lark
from lark import Lark, Token
from lark import UnexpectedInput, UnexpectedCharacters, UnexpectedToken

from protogen.util import PGToken
from protogen.transformer import PGTransformer
from protogen.compiler import PythonCompiler

from typing import List
import glob
import os
import sys
from pprint import pprint


class PGParser(object):
    def __init__(self, syntaxPath: str = 'grammar/proto_gen.lark',
                 inputs: List[str] = None):

        if len(inputs) == 0:
            print('You must specify at least one valid input file '
                  '(glob patterns are accepted).')
            print('Example:\n *.protogen input/example.protogen')
            sys.exit(1)

        # Variables
        self.files = []

        # Clean up and list input files.
        self._files = {}
        files_to_compile = set()
        for items in inputs:
            for item in glob.glob(items):
                files_to_compile.add(item)
                self._files[item] = None

        with open(os.path.join(os.path.dirname(__file__),
                               syntaxPath), 'r') as file:
            grammar = file.read()

        self._parser = Lark(grammar=grammar, parser='lalr',
                            propagate_positions=True)

    def parse(self):
        for item in self._files:
            try:
                with open(item, 'r') as data:
                    self._files[item] = self._parser.parse(data.read())
                    # MyTransformer().transform(parser._files[item])
            except IsADirectoryError as e:
                print('You must specify files. For multiple files in a '
                      'directory, a glob pattern may be used.')
                print('Example: directory/*.protogen')
                sys.exit(2)

    def transform(self):
        self._trees = {}
        for file in self._files:
            self._trees[file] = PGTransformer().transform(self._files[file])
            # pprint(self._trees[file])
        test = None
        for tree in self._trees:
            # len(_files) == len(_trees) AND order == 'same'
            test = PGFile(tree, self._trees[tree])

        myCompiler = PythonCompiler(test)

    def display(self):
        for item in self._files:
            print("--- BEGIN FILE: {} ---".format(item))
            print(self._files[item].pretty())
            print("---   END FILE: {} ---".format(item))

    def _display(self):
        for item in self._files:
            print("--- BEGIN FILE: {} ---".format(item))
            print(self._files[item])
            print("---   END FILE: {} ---".format(item))

    def pretty(self):
        pprint(self._files)


# class PGTree(object):
#     def __init__(self):
#         self.headers = []

#     def reform(self, trees):
#         for tree in trees:  # [{tree}, {}, ...] Trees
#             for item in trees[tree]:
#                 for thing in item:
#                     print(thing)
#                     print(item)
#                     if thing is Tokens.HEADER_NAME:
#                         self.headers.append(item[thing])
#                     elif thing == Tokens.INCLUDE:
#                         pass
#         print(self.headers)


class PGFile(object):
    def __init__(self, path, tree):
        self.filename = path
        self.header = None
        self.includes = []
        self.declarations = {}
        self.types = []

        self.buildFile(tree)

        # self.compilePython()

    def buildFile(self, tree):
        for tree_item in tree:
            for token in tree_item:
                if token is PGToken.HEADER_NAME:
                    self.header = tree_item[token]
                elif token is PGToken.INCLUDE:
                    self.includes.append(tree_item[token])
                elif token is PGToken.TYPE_BLOCK:
                    # print("tree_item:", tree_item)
                    # print("tree_item[token]", tree_item[token])
                    self.processTypeBlock(None, tree_item[token],
                                          tree_item[token])
                else:
                    print("Bad token!")

        pprint({"name": self.filename,
                "header": self.header,
                "includes": self.includes,
                "declarations": self.declarations,
                "types": self.types})

    def processTypeBlock(self, parent_type, parent_type_block,
                         current_type_block):
        if parent_type_block == current_type_block:
            parent_type = current_type_block[0]
            self.types.append((current_type_block[0], None, parent_type))
        else:
            parent_type += '.' + current_type_block[0]
            self.types.append((current_type_block[0], parent_type_block[0],
                              parent_type))

        for tokens in current_type_block:
            for token in tokens:
                if token is PGToken.DECLARATION:
                    fullType = parent_type + '.' + tokens[token][0]
                    self.declarations[fullType] = (tokens[token][1],
                                                   tokens[token][2])
                if token is PGToken.TYPE_BLOCK:
                    self.processTypeBlock(
                        parent_type, current_type_block, tokens[token])


    # def compilePython(self):
    #     i = "    "  # shorthand for indent
    #     classItems = set()
    #     declarations = list(self.declarations.keys())
    #     for key, item in enumerate(declarations):
    #         declarations[key] = item.split('.')

    #     while len(declarations) > 0:
    #         for key, item in enumerate(declarations):
    #             if len(item) == 2:
    #                 pass
