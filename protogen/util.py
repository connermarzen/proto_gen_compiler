from enum import Enum
from typing import List, Literal


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


class PyClass(object):
    def __init__(self, name: str, fqname: str):
        self.name = name
        self.fqname = fqname
        self.parent = None
        self.subclasses: List[self] = []

    def __str__(self) -> str:

        return ('Shorthand Name:       {}\n'
                'Fully Qualified Name: {}\n'
                'Parent Class:         {}\n'
                'Child Classes:        {}\n'.format(
                    self.name,
                    self.fqname,
                    self.parent.fqname if self.parent else None,
                    self.gatherSubclasses('name')))

    def gatherSubclasses(self, attribute: Literal['name', 'fqname', 'parent']):
        results = {}
        if attribute == 'name':
            for pclass in self.subclasses:
                results[pclass.name] = pclass
        elif attribute == 'parent':
            for pclass in self.subclasses:
                results[pclass.parent] = pclass
        elif attribute == 'fqname':
            for pclass in self.subclasses:
                results[pclass.fqname] = pclass
        else:
            raise AttributeError
        return results


class PGFile(object):
    def __init__(self, path, tree):
        self.filename = path
        self.header = None
        self.classes: List[PyClass] = []
        self.includes = []
        self.declarations = {}
        self.types = []
        
        self.buildFile(tree)
        self.buildClasses()

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

    def buildClasses(self):
        # s.f.types[:] -> List[(class, parentClass, fullyQualifiedClassName)]
        for item in self.types[:]:
            self.classes.append(PyClass(item[0], item[2]))
            last = self.classes[-1]
            if item[1] in self.gatherClasses('name'):
                self.findClassByName(inferParentClass(
                    item[2])).subclasses.append(last)
                last.parent = self.findClassByName(
                    inferParentClass(last.fqname))

    def gatherClasses(self, attribute: Literal["name", "fqname", "parent"]):
        results = {}
        if attribute == 'name':
            for pyClass in self.classes:
                results[pyClass.name] = pyClass
        elif attribute == 'parent':
            for pyClass in self.classes:
                results[pyClass.parent] = pyClass
        elif attribute == 'fqname':
            for pyClass in self.classes:
                results[pyClass.fqname] = pyClass
        else:
            raise AttributeError
        return results

    def findClassByName(self, query: str) -> PyClass:
        for item in self.classes:
            if item.fqname == query:
                return item
        return None


def inferParentClass(fullyQualName: str):
    return fullyQualName[:fullyQualName.rfind('.')]


def inferShortName(fullyQualName: str):
    return fullyQualName[fullyQualName.rfind('.')+1:]


def getVarName(name: str, required: bool):
    if required:
        return '_r_{}'.format(name)
    else:
        return '_o_{}'.format(name)
