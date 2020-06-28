from lark import Lark
from lark import UnexpectedInput, UnexpectedCharacters, UnexpectedToken, Token
from typing import List

import os


class Parser(object):
    def __init__(self, syntaxPath: str = None, inputs: List[str] = None):
        with open(os.path.join(os.path.dirname(__file__),
                               'grammar/proto_gen.lark'), 'r') as file:
            grammar = file.read()
        self._parser = Lark(grammar=grammar, parser='lalr',
                            propagate_positions=True)
        self._files = inputs
        self.data = []

    def parse(self):
        for item in self._files:
            with open(item, 'r') as data:
                self.data.append(self._parser.parse(data.read()))

    def display(self):
        for item in self.data:
            print(item.pretty())


def main():

    # with open("syntax.lark", 'r') as file:
    #     lingo = file.read()
    with open(os.path.join(os.path.dirname(__file__), "testfile.protogen"), 'r') as file:
        data = file.read()

    tester = Parser()

    print(tester._parser.parse(data).pretty())

    # datalines = data.splitlines()
    # parser = Lark(grammar=lingo, propagate_positions=True, parser="lalr")

    # try:
    #     stuff = parser.parse(data)
    # except UnexpectedInput as u:
    #     print(u)
    #     # print("--- Parsing Error ---")
    #     # print("Line:   {}\nColumn: {}".format(u.line, u.column))
    #     # print()
    #     # print(datalines[u.line - 1])
    #     # print(" "*(u.column - 1) + "^\n")

    #     # if type(u) is UnexpectedCharacters:
    #     #     if 'HEADER_NAME' in u.allowed:
    #     #         print("The package name must consist of only letters,"
    #     #               " and start with a capital letter.")
    #     # elif type(u) is UnexpectedToken:
    #     #     if 'HEADER_NAME' in u.expected:
    #     #         print("A capitalized package name is expected. Example:\n")
    #     #         print("name MyPackage;")
    #     #         print("name Sample;")
    #     #     if 'DELIMETER' in u.expected:
    #     #         print("Extra data in line, needs removed.")
    #     #     if 'TYPE' in u.expected:
    #     #         print("Syntax error, 'type' expected.")

    # print(stuff.pretty())
    # for item in stuff.iter_subtrees_topdown():
    #     print("Token: {}\n Data: {}\n".format(item.data, item.children[0]))

    # files_to_import = []
    # for item in stuff.find_data("include"):
    #     files_to_import.append(str(item.children[0]).strip("'"))

    # for item in files_to_import:
    #     print(item)
