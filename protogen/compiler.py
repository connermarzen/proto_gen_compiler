from typing import List, Literal, Tuple

import protogen.util as util
from protogen.library.std import STANDARD_TYPES
from protogen.util import PGFile, PyClass


class PythonCompiler(object):

    # def __init__(self, files: List[PGFile]):
    def __init__(self, files: List[PGFile]):
        self.classes: List[PyClass] = []
        # self.files: List[PGFile] = files
        self.files: List[PGFile] = files
        for item in self.files:
            self.generateCode(file=item)

    def printClass(self, file: PGFile, pyClass: PyClass,
                   indent: int, root: bool):
        tab = '    '
        if root:
            print("\nclass {}(Message, Serializable, "
                  "Printable):".format(pyClass.name))
        else:
            print("\n{}class {}(Printable):".format(tab*indent, pyClass.name))
        # print("{}".format(ind*mul))
        # print("{}pass".format(ind*(mul+2)))
        print("\n{}def __init__(self):".format(tab*(indent+1)))
        self.printAttributes(file, pyClass, indent+1)
        for item in pyClass.subclasses:
            self.printClass(file, item, indent+1, False)

        self.printMethods(file, pyClass, indent+1)
        print("{}# End Class {}".format(tab*indent, pyClass.name))

    def printAttributes(self, file: PGFile, pyClass: PyClass, indent: int):
        tab = '    '
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                thing = file.declarations[item]
                short = util.inferShortName(item)
                if thing[1]:  # if the type is required.
                    # primitive data type
                    if thing[0] in STANDARD_TYPES.values():
                        print('{}self._r_{}: {} = None'.format(
                            tab*(indent+1), short, thing[0]))

                    # local, nested class (needs 'self')
                    elif thing[0] in pyClass.gatherSubclasses('name'):
                        print('{}self._r_{}: self.{} = self.{}()'.format(
                            tab*(indent+1), short, thing[0], thing[0]))

                    # local, non-nested class (doesn't need 'self')
                    else:
                        print('{}self._r_{}: {} = {}()'.format(
                            tab*(indent+1), short, thing[0], thing[0]))

                else:  # if the type is optional
                    # primitive data type
                    if thing[0] in STANDARD_TYPES.values():
                        print('{}self._o_{}: {} = None'.format(
                            tab*(indent+1), short, thing[0]))

                    # local, nested class
                    elif thing[0] in pyClass.gatherSubclasses('name'):
                        print('{}self._o_{}: self.{} = None'.format(
                            tab*(indent+1), short, thing[0]))

                    # local, non-nested class (doesn't need 'self')
                    else:
                        print('{}self._o_{}: {} = None'.format(
                            tab*(indent+1), short, thing[0]))

    def printMethods(self, file: PGFile, pyClass: PyClass, indent: int):
        tab = '    '
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                thing = file.declarations[item]
                short = util.inferShortName(item)

                # Get methods
                if thing[0] in STANDARD_TYPES.values():
                    print('\n{}def get{}(self) -> {}:'.format(
                        (tab*indent), short.capitalize(), thing[0]))
                else:
                    print('\n{}def get{}(self) -> {}:'.format(
                        (tab*indent), short.capitalize(), thing[0]))
                print('{}return self.{}'.format(
                    (tab*(indent+1)), util.getVarName(short, thing[1])))

                # Set methods
                print('\n{}def set{}(self, {}: {}) -> \'{}\':'.format(
                    (tab*indent), short.capitalize(),
                    short, thing[0], pyClass.name))
                print('{}self.{} = {}'.format(
                    (tab*(indent+1)), util.getVarName(
                        short, thing[1]), short))
                print('{}return self'.format((tab*(indent+1))))

    def generateCode(self, file: PGFile, indent: str = '    '):
        print("from protogen.library.message import Message")
        print("from protogen.library.message import Serializable")
        print("from protogen.library.message import Printable\n")
        for item in file.classes:
            if item.parent is None:
                self.printClass(file, item, 0, True)
