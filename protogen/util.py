from enum import Enum


class PGToken(Enum):
    DECLARATION = 1
    TYPE_BLOCK = 2
    DATA_TYPE = 3
    HEADER_NAME = 4
    NAME = 5
    REQ = 6
    OPT = 7
    REQUIRED = 8
    INCLUDE = 9


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
