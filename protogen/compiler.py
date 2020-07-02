from typing import List, Literal, Tuple
from pprint import pprint
# from protogen.core import PGFile


class PythonCompiler(object):

    def __init__(self, file: 'protogen.core.PGFile'):
        self.classes: List[self.PyClass] = []
        self.file: 'protogen.core.PGFile' = file
        self.buildClasses()
        self.generateCode(indent="    ")

    class PyClass(object):
        def __init__(self, name: str, fqname: str):
            self.name = name
            self.fqname = fqname
            self.parent = None
            self.subclasses: 'protogen.compiler.PythonCompiler.PyClass' = []

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

    class PyAttribute(object):
        def __init__(self):
            self.name: str = None
            self.type: str = None
            self.req: bool = None

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

    def printClass(self, pyClass, indent: Tuple[str, int], root: bool):
        ind, mul = indent
        if root:
            print("class {}(Message, Serializable, "
                  "Printable):".format(pyClass.name))
        else:
            print("{}class {}(Printable):".format(ind*mul,
                                                  pyClass.name))
        print("{}".format(ind*mul))
        print("{}def __init__(self):".format(ind*(mul+1)))
        print("{}pass".format(ind*(mul+2)))
        print("{}".format(ind*mul))

        for item in pyClass.subclasses:
            self.printClass(item, (ind, mul+1), False)

    def generateCode(self, indent: str):
        print("from protogen.library.message import Message")
        print("from protogen.library.message import Serializable")
        print("from protogen.library.message import Printable\n")
        for item in self.classes:
            if item.parent is None:
                self.printClass(item, (indent, 0), True)

    @ staticmethod
    def inferParentClass(fullyQualName: str):
        return fullyQualName[:fullyQualName.rfind('.')]

    def buildMethods(self, in_class: PyClass):
        pass

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
