from typing import List, Literal, Tuple, Iterable
from pprint import pprint
from protogen.util import PGFile
from protogen.library.std import STANDARD_TYPES


class PythonCompiler(object):

    def __init__(self, file: PGFile):
        self.classes: List[self.PyClass] = []
        self.file: PGFile = file
        self.buildClasses()
        self.generateCode(indent="    ")

    class PyClass(object):
        def __init__(self, name: str, fqname: str):
            self.name = name
            self.fqname = fqname
            self.parent = None
            self.subclasses: List[self] = []

        def __str__(self) -> str:
            subclasses = []
            for item in self.subclasses:
                subclasses.append(item.fqname)

            if self.parent is not None:
                return ('Shorthand Name:       {}\n'
                        'Fully Qualified Name: {}\n'
                        'Parent Class:         {}\n'
                        'Child Classes:        {}\n'.format(
                            self.name, self.fqname,
                            self.parent.fqname, subclasses))
            else:
                return ('Shorthand Name:       {}\n'
                        'Fully Qualified Name: {}\n'
                        'Parent Clcass:        {}\n'
                        'Child Classes:        {}\n'.format(
                            self.name, self.fqname,
                            None, subclasses))

    def buildClasses(self):
        # s.f.types[:] -> List[(class, parentClass, fullyQualifiedClassName)]
        for key, item in enumerate(self.file.types[:]):
            self.classes.append(self.PyClass(item[0], item[2]))
            last = self.classes[-1]
            if item[1] in self.gatherClasses('name'):
                self.findClassByName(
                    self.inferParentClass(
                        item[2])).subclasses.append(last)

                last.parent = self.findClassByName(
                    self.inferParentClass(last.fqname))

    def printClass(self, pyClass: PyClass,
                   indent: Tuple[str, int], root: bool):
        ind, mul = indent  # indentation, multiplier (for indentation)
        print('\n')
        if root:
            print("class {}(Message, Serializable, "
                  "Printable):".format(pyClass.name))
        else:
            print("{}class {}(Printable):".format(ind*mul,
                                                  pyClass.name))
        # print("{}".format(ind*mul))
        # print("{}pass".format(ind*(mul+2)))
        print("\n{}def __init__(self):".format(ind*(mul+1)))
        self.printAttributes(pyClass, (ind, mul+1))
        for item in pyClass.subclasses:
            self.printClass(item, (ind, mul+1), False)

        self.printMethods(pyClass, (ind, mul+1))

    def printAttributes(self, pyClass: PyClass, indent: Tuple[str, int]):
        ind, mul = indent  # indentation, multiplier (for indentation)
        for item in self.file.declarations:
            if self.inferParentClass(item) == pyClass.fqname:
                thing = self.file.declarations[item]
                short = self.inferShortName(item)
                if thing[1]:  # if the type is required.
                    # primitive data type
                    if thing[0] in STANDARD_TYPES.values():
                        print('{}self._r_{}: {} = None'.format(
                            ind*(mul+1), short, thing[0]))

                    # local, nested class (needs 'self')
                    elif thing[0] in self.gatherSubclasses(pyClass, 'name'):
                        print('{}self._r_{}: self.{} = self.{}()'.format(
                            ind*(mul+1), short, thing[0], thing[0]))

                    # local, non-nested class (doesn't need 'self')
                    else:
                        print('{}self._r_{}: {} = {}()'.format(
                            ind*(mul+1), short, thing[0], thing[0]))

                else:  # if the type is optional
                    # primitive data type
                    if thing[0] in STANDARD_TYPES.values():
                        print('{}self._o_{}: {} = None'.format(
                            ind*(mul+1), short, thing[0]))

                    # local, nested class
                    elif thing[0] in self.gatherSubclasses(pyClass, 'name'):
                        print('{}self._o_{}: self.{} = None'.format(
                            ind*(mul+1), short, thing[0]))

                    # local, non-nested class (doesn't need 'self')
                    else:
                        print('{}self._o_{}: {} = None'.format(
                            ind*(mul+1), short, thing[0]))

    def printMethods(self, pyClass: PyClass, indent: Tuple[str, int]):
        ind, mul = indent
        for item in self.file.declarations:
            if self.inferParentClass(item) == pyClass.fqname:
                thing = self.file.declarations[item]
                short = self.inferShortName(item)

                # Get methods
                if thing[0] in STANDARD_TYPES.values():
                    print('\n{}def get{}(self) -> {}:'.format(
                        (ind*mul), short.capitalize(), thing[0]))
                else:
                    print('\n{}def get{}(self) -> {}:'.format(
                        (ind*mul), short.capitalize(), thing[0]))
                print('{}return self.{}'.format(
                    (ind*(mul+1)), self.getVarName(short, thing[1])))

                # Set methods
                print('\n{}def set{}(self, {}: {}) -> \'{}\':'.format(
                    (ind*mul), short.capitalize(),
                    short, thing[0], pyClass.name))
                print('{}self.{} = {}'.format(
                    (ind*(mul+1)), self.getVarName(
                        short, thing[1]), short))
                print('{}return self'.format((ind*(mul+1))))

    def generateCode(self, indent: str):
        print("from protogen.library.message import Message")
        print("from protogen.library.message import Serializable")
        print("from protogen.library.message import Printable")
        for item in self.classes:
            if item.parent is None:
                self.printClass(item, (indent, 0), True)

    @staticmethod
    def inferParentClass(fullyQualName: str):
        return fullyQualName[:fullyQualName.rfind('.')]

    @staticmethod
    def inferShortName(fullyQualName: str):
        return fullyQualName[fullyQualName.rfind('.')+1:]

    @staticmethod
    def getVarName(name: str, required: bool):
        if required:
            return '_r_{}'.format(name)
        else:
            return '_o_{}'.format(name)

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

    def gatherSubclasses(self, pyClass: PyClass,
                         attribute: Literal['name', 'fqname', 'parent']):
        results = {}
        if attribute == 'name':
            for pclass in pyClass.subclasses:
                results[pclass.name] = pclass
        elif attribute == 'parent':
            for pclass in pyClass.subclasses:
                results[pclass.parent] = pclass
        elif attribute == 'fqname':
            for pclass in pyClass.subclasses:
                results[pclass.fqname] = pclass
        else:
            raise AttributeError
        return results

    def findClassByName(self, query: str) -> PyClass:
        for item in self.classes:
            if item.fqname == query:
                return item
        return None
