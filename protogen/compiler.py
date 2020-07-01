from typing import List, Literal
from pprint import pprint


class PythonCompiler(object):
    class PyClass(object):
        def __init__(self, name: str, fqname: str):
            self.name = name
            self.fqname = fqname
            self.parent = None
            self.subclasses: 'protogen.compiler.PythonCompiler.PyClass' = []

        def __str__(self) -> str:
            if self.parent is not None:
                return ('Shorthand Name:       {}\n'
                        'Fully Qualified Name: {}\n'
                        'Parent Class:         {}\n'
                        'Child Classes:        {}\n'.format(
                            self.name, self.fqname,
                            self.parent.fqname, self.subclasses))
            else:
                return ('Shorthand Name:       {}\n'
                        'Fully Qualified Name: {}\n'
                        'Parent Clcass:        {}\n'
                        'Child Classes:        {}\n'.format(
                            self.name, self.fqname,
                            None, self.subclasses))

    class PyAttribute(object):
        def __init__(self):

            self.name: str = None
            self.type: str = None
            self.req: bool = None

    def __init__(self, file: 'protogen.core.PGFile'):
        self.classes: List[self.PyClass] = []
        self.file: 'protogen.core.PGFile' = file
        self.buildClasses()
        # TODO HERE!

    def buildClasses(self):
        # s.f.types[:] -> List[(class, parentClass, fullyQualifiedClassName)]
        for key, item in enumerate(self.file.types[:]):
            if item[1] is None:
                self.classes.append(self.PyClass(item[0], item[2]))
            elif item[1] in self.gatherClasses('name'):
                self.classes.append(self.PyClass(item[0], item[2]))
                self.classes[-1].parent = self.findClassByName(
                    self.inferParentClass(
                        self.classes[-1].fqname))
                self.findClassByName(
                    item[2]).subclasses.append(self.classes[-1])

        for item in self.classes:
            print(item)

    @staticmethod
    def inferParentClass(fullyQualName: str):
        return fullyQualName[:fullyQualName.rfind('.')]

    def buildMethods(self, in_class: PyClass):
        pass

    def gatherClasses(self, attribute: Literal["name", "parent"]):
        results = {}
        if attribute == 'name':
            for pyClass in self.classes:
                results[pyClass.name] = pyClass
        elif attribute == 'parent':
            for pyClass in classes:
                results[pyClass.parent] = pyClass
        else:
            raise AttributeError
        return results

    def findClassByName(self, query: str) -> PyClass:
        for item in self.classes:
            if item.fqname == query:
                return item
        return None
