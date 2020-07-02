import glob
import os
import sys
from pprint import pprint
from typing import List

from lark import Lark

from protogen.compiler import PythonCompiler
from protogen.transformer import PGTransformer
from protogen.util import PGToken


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

        return test


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


class PGFile(object):
    def __init__(self, path, tree):
        self.filename = path
        self.header = None
        self.includes = []
        self.declarations = {}
        self.types = []
        self.buildFile(tree)

    def buildFile(self, tree):
        for tree_item in tree:
            for token in tree_item:
                if token is PGToken.HEADER_NAME:
                    self.header = tree_item[token]
                elif token is PGToken.INCLUDE:
                    self.includes.append(tree_item[token])
                elif token is PGToken.TYPE_BLOCK:
                    self.processTypeBlock(None, None,
                                          tree_item[token])
                else:
                    print("Bad token!")

        # pprint({"name": self.filename,
        #         "header": self.header,
        #         "includes": self.includes,
        #         "declarations": self.declarations,
        #         "types": self.types})

    def processTypeBlock(self, fqname, parent_type_block,
                         current_type_block):
        if parent_type_block is None:
            fqname = current_type_block[0]
        else:
            fqname += '.' + current_type_block[0]

        self.types.append((current_type_block[0],
                           (parent_type_block[0]
                            if parent_type_block is not None else None),
                           fqname))

        for tokens in current_type_block:
            for token in tokens:
                if token is PGToken.DECLARATION:
                    fullType = fqname + '.' + tokens[token][0]
                    self.declarations[fullType] = (tokens[token][1],
                                                   tokens[token][2])
                elif token is PGToken.TYPE_BLOCK:
                    self.processTypeBlock(
                        fqname, current_type_block, tokens[token])
