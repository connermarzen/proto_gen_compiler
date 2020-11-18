import os
from io import TextIOWrapper
from typing import List

import protogen.util as util
from protogen.compiler import Compiler
from protogen.compiler import tab as tab
from protogen.library.python.std import ACCEPTED_TYPES, PYTHON_TYPES
from protogen.util import PGFile, PyClass


class PythonCompiler(Compiler):

    def __init__(self, inFiles: List[str], outDir: str, verbose: bool = False):
        super().__init__(inFiles, outDir, verbose)

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
        if root:
            out.write(f"\nclass {pyClass.name}(Serializable, Printable):\n")
        else:
            out.write(
                f"\n{tab*indent}class {pyClass.name}(Serializable, Printable):\n")
        out.write(
            f"\n{tab*(indent+1)}def __init__(self, data: dict = None):\n")
        self.printAttributes(out, file, pyClass, indent+1)
        out.write(f"\n{tab*(indent+2)}if data is not None:\n")
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                short = util.inferShortName(item)
                v_type, required = file.declarations[item]
                if v_type in ACCEPTED_TYPES:
                    out.write(
                        f"{tab*(indent+3)}self.data['{short}'][0] = data['{short}']\n")
                # local, nested class (needs 'self')
                elif v_type in pyClass.gatherSubclasses('name'):
                    out.write(
                        f"{tab*(indent+3)}self.data['{short}'][0] = self.{v_type}(data['{short}'])\n")
                # local, non-nested class (doesn't need 'self')
                else:
                    out.write(
                        f"{tab*(indent+3)}self.data['{short}'][0] = {v_type}(data['{short}'])\n")

        for item in pyClass.subclasses:
            self.printClass(out, file, item, indent+1, False)

        self.printMethods(out, file, pyClass, indent+1)
        out.write(f"{tab*indent}# End Class {pyClass.name}\n")

    def printAttributes(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int):
        out.write(f'{tab*(indent+1)}self.data = {{\n')
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                v_type, required = file.declarations[item]
                short = util.inferShortName(item)
                # primitive data type
                if v_type == 'list':
                    out.write(
                        f'{tab*(indent+2)}\'{short}\': [[], {required}, False],\n')
                elif v_type == 'map':
                    out.write(
                        f'{tab*(indent+2)}\'{short}\': [{{}}, {required}, False],\n')
                elif v_type in ACCEPTED_TYPES:
                    out.write(
                        f'{tab*(indent+2)}\'{short}\': [None, {required}, False],\n')
                # local, nested class (needs 'self')
                elif v_type in pyClass.gatherSubclasses('name'):
                    out.write(
                        f'{tab*(indent+2)}\'{short}\': [self.{v_type}(), {required}, True],\n')
                # local, non-nested class (doesn't need 'self')
                else:
                    out.write(
                        f'{tab*(indent+2)}\'{short}\': [{v_type}(), {required}, True],\n')

        out.write(f'{tab*(indent+1)}}}\n')

    def printMethods(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int):
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                v_type, req = file.declarations[item]
                short = util.inferShortName(item)

                # Get methods
                if v_type in ACCEPTED_TYPES:
                    out.write(
                        f'\n{tab*indent}def get_{short}(self) -> {PYTHON_TYPES[v_type]}:\n')
                else:
                    out.write(
                        f'\n{tab*indent}def get_{short}(self) -> {v_type}:\n')
                out.write(
                    f'{tab*(indent+1)}return self.data[\'{short}\'][0]\n')

                # Set methods
                if v_type in PYTHON_TYPES:
                    out.write(
                        f'\n{tab*indent}def set_{short}(self, {short}: {PYTHON_TYPES[v_type]}) -> \'{pyClass.name}\':\n'
                        f'{tab*(indent+1)}self._assertType("{short}", {short}, {PYTHON_TYPES[v_type]}, "{v_type}")\n')
                else:
                    out.write(
                        f'\n{tab*indent}def set_{short}(self, {short}: {v_type}) -> \'{pyClass.name}\':\n')
                out.write(
                    f'{tab*(indent+1)}self.data[\'{short}\'][0] = {short}\n'
                    f'{tab*(indent+1)}return self\n')

    def printFactory(self, out: TextIOWrapper, file: PGFile):
        outString = (
            "\n\nclass {}Factory(object):\n"
            "    @staticmethod\n"
            "    def deserialize(data: bytes):\n"
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
                out.write(f'{tab*3}if packetType == \'{item.name}\':\n'
                          f'{tab*4}return {item.name}(data[item])\n')

        out.write(
            "            else:\n"
            "                raise AttributeError('Respective class not found.')\n")

    def generateCode(self, out: TextIOWrapper, file: PGFile):
        out.write("from protogen.library.python.message import Serializable\n"),
        out.write("from protogen.library.python.message import Printable\n\n")
        for item in file.classes:
            if item.parent is None:
                self.printClass(out, file, item, 0, True)
        self.printFactory(out, file)
