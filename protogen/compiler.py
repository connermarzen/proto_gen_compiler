import os
from io import TextIOWrapper
from typing import List

import protogen.util as util
from protogen.core import PGParser
from protogen.library.std import STANDARD_TYPES
from protogen.util import PGFile, PyClass


class PythonCompiler(object):

    def __init__(self, inFiles: List[str], outDir: str, verbose: bool = False):
        self._parser = PGParser(inFiles)
        self._parser.parse()

        if not os.path.exists(outDir):
            os.makedirs(outDir)
        # remove tailing slash for consistency (I will add them back in)
        self.outDir = outDir.rstrip('/')

        self.classes: List[PyClass] = []
        self.files: List[PGFile] = self._parser.transform()
        del(self._parser)  # save memory, the parser is dense and repetitive

        # TODO: Work through parser and consolidate into PythonCompiler

    def compile(self):
        for item in self.files:
            print('Compiling {} into {}/{}_proto.py'
                  ''.format(item.filename, self.outDir, item.header))
            file = open(self.outDir + '/' + item.header + '_proto.py', 'w')
            self.generateCode(out=file, file=item)
            file.write(os.linesep)
            file.close()

    def printClass(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass,
                   indent: int, root: bool):
        tab = '    '
        if root:
            out.write("\nclass {}(Message, Serializable, "
                      "Printable):\n".format(pyClass.name))
        else:
            out.write("\n{}class {}(Printable):\n".format(
                tab*indent, pyClass.name))
        # print("{}".format(ind*mul))
        # print("{}pass".format(ind*(mul+2)))
        out.write("\n{}def __init__(self, data: dict = None):\n"
                  .format(tab*(indent+1)))
        self.printAttributes(out, file, pyClass, indent+1)
        if root:
            out.write("\n{}if data is not None:\n".format(tab*(indent+2)))
            out.write("{}self._init(self, data)\n".format(tab*(indent+3), ))
        for item in pyClass.subclasses:
            self.printClass(out, file, item, indent+1, False)

        self.printMethods(out, file, pyClass, indent+1)
        out.write("{}# End Class {}\n".format(tab*indent, pyClass.name))

    def printAttributes(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int):
        tab = '    '
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                thing = file.declarations[item]
                short = util.inferShortName(item)
                if thing[1]:  # if the type is required.
                    # primitive data type
                    if thing[0] in STANDARD_TYPES.values():
                        out.write('{}self._r_{}: {} = None\n'.format(
                            tab*(indent+1), short, thing[0]))

                    # local, nested class (needs 'self')
                    elif thing[0] in pyClass.gatherSubclasses('name'):
                        out.write('{}self._r_{}: self.{} = self.{}()\n'.format(
                            tab*(indent+1), short, thing[0], thing[0]))

                    # local, non-nested class (doesn't need 'self')
                    else:
                        out.write('{}self._r_{}: {} = {}()\n'.format(
                            tab*(indent+1), short, thing[0], thing[0]))

                else:  # if the type is optional
                    # primitive data type
                    if thing[0] in STANDARD_TYPES.values():
                        out.write('{}self._o_{}: {} = None\n'.format(
                            tab*(indent+1), short, thing[0]))

                    # local, nested class
                    elif thing[0] in pyClass.gatherSubclasses('name'):
                        out.write('{}self._o_{}: self.{} = None\n'.format(
                            tab*(indent+1), short, thing[0]))

                    # local, non-nested class (doesn't need 'self')
                    else:
                        out.write('{}self._o_{}: {} = None\n'.format(
                            tab*(indent+1), short, thing[0]))

    def printMethods(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int):
        tab = '    '
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                thing = file.declarations[item]
                short = util.inferShortName(item)

                # Get methods
                if thing[0] in STANDARD_TYPES.values():
                    out.write('\n{}def get{}(self) -> {}:\n'.format(
                        (tab*indent), short.capitalize(), thing[0]))
                else:
                    out.write('\n{}def get{}(self) -> {}:\n'.format(
                        (tab*indent), short.capitalize(), thing[0]))
                out.write('{}return self.{}\n'.format(
                    (tab*(indent+1)), util.getVarName(short, thing[1])))

                # Set methods
                out.write('\n{}def set{}(self, {}: {}) -> \'{}\':\n'.format(
                    (tab*indent), short.capitalize(),
                    short, thing[0], pyClass.name))
                out.write('{}self.{} = {}\n'.format(
                    (tab*(indent+1)), util.getVarName(
                        short, thing[1]), short))
                out.write('{}return self\n'.format((tab*(indent+1))))

    def printFactory(self, out: TextIOWrapper, file: PGFile):
        tab = '    '
        outString = (
            "\n\nclass {}Factory(object):\n"
            "    @staticmethod\n"
            "    def deserialize(data: bytes) -> Message:\n"
            "        data = Serializable.deserialize(data)\n"
            "        if len(data) > 1:\n"
            "            raise AttributeError('This is likely not a Protogen packet.')\n"
            "\n"
            "        packetType = None\n"
            "        for item in data:\n"
            "            packetType = item[item.rfind('.')+1:]\n"
        )
        out.write(outString.format(file.header))
        for item in file.classes:
            if item.parent is None:  # root-level class
                out.write('{}if packetType == \'{}\':\n'.format(
                    tab*3, item.name))
                out.write('{}return {}(data[item])\n'.format(tab*4, item.name))
        outString = (
            "            else:\n"
            "                raise AttributeError('Respective class not found.')\n"
        )
        out.write(outString)

    def generateCode(self, out: TextIOWrapper, file: PGFile, indent: str = '    '):
        out.write("from protogen.library.message import Message\n")
        out.write("from protogen.library.message import Serializable\n"),
        out.write("from protogen.library.message import Printable\n\n")
        for item in file.classes:
            if item.parent is None:
                self.printClass(out, file, item, 0, True)
        self.printFactory(out, file)
