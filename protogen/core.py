from lark import Lark, Token, Transformer
from lark import UnexpectedInput, UnexpectedCharacters, UnexpectedToken

from typing import List
import glob
import os
import sys
from pprint import pprint
from enum import Enum


class ProtoTokens(Enum):
    DECLARATION = 1
    TYPE_BLOCK = 2
    DATA_TYPE = 3
    HEADER_NAME = 4
    NAME = 5
    REQ = 6
    OPT = 7
    REQUIRED = 8
    INCLUDE = 9


class ProtoTransformer(Transformer):
    def header(self, item):
        (item,) = item
        return item

    def start(self, items): return list(items)

    def declaration(self, items): return {ProtoTokens.DECLARATION: items}

    def type_block(self, items): return {ProtoTokens.TYPE_BLOCK: items}

    def data_opt(self, item):
        if len(item) > 0:
            return {ProtoTokens.REQUIRED: item[0]}
        return {ProtoTokens.REQUIRED: False}

    def include(self, item): return {ProtoTokens.INCLUDE: item[0]}

    def data_type(self, item):
        if item[0] == 'req' or item[0] == 'opt':
            raise SyntaxError('DATATYPE Expected, '
                              'received {}'.format(item[0]))
        return {ProtoTokens.DATA_TYPE: item[0]}

    def HEADER_NAME(self, item: Token):
        return {ProtoTokens.HEADER_NAME: item.value}

    def name(self, item): return {ProtoTokens.NAME: item[0]}
    def DATATYPE(self, item: Token): return item.value
    def REQUIRED(self, item): return True
    def OPTIONAL(self, item): return False
    def ESCAPED_STRING(self, item): return item.strip("'").strip('"')
    def QNAME(self, item): return self.ESCAPED_STRING(item)


class ProtogenParser(object):
    def __init__(self, syntaxPath: str = 'grammar/proto_gen.lark',
                 inputs: List[str] = None):

        if len(inputs) == 0:
            print('You must specify at least one valid input file '
                  '(glob patterns are accepted).')
            print('Example:\n *.protogen input/example.protogen')
            sys.exit(1)

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
        for item in self._files:
            self._trees[item] = ProtoTransformer().transform(self._files[item])

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
