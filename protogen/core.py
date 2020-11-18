import glob
import os
import sys
from pprint import pprint
from typing import List

from lark import Lark

from protogen.grammar.transformer import PGTransformer
from protogen.util import PGFile


class PGParser(object):
    def __init__(self, inputs: List[str],
                 syntaxPath: str = 'grammar/proto_gen.lark'):

        # Clean up and list input files.
        self._files = {}
        for items in inputs:
            for item in glob.glob(items):
                self._files[item] = None  # Add placeholder in dict for parsing

        if len(self._files) == 0:
            print('No valid files were specified.')
            print('Note: a glob pattern is acceptible for multiple files.\n')
            print('Example:\n  *.protogen\n')
            print('You can also specify more than one file, '
                  'separated by spaces.\n')
            print('Example:\n  a.protogen b.protogen c.protogen')

            sys.exit(1)

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
        outfiles = []
        for tree in self._trees:
            # len(_files) == len(_trees) AND order == 'same'
            outfiles.append(PGFile(tree, self._trees[tree]))
        return outfiles

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
