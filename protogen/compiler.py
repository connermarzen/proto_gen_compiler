import os
from io import TextIOWrapper
from typing import List

import protogen.util as util
from protogen.core import PGParser
from protogen.library.std import ACCEPTED_TYPES, JS_TYPES, PYTHON_TYPES
from protogen.util import PGFile, PyClass

tab = '    '


class Compiler(object):

    def __init__(self, inFiles: List[str], outDir: str, verbose: bool = False):
        self._parser = PGParser(inFiles)
        self._parser.parse()

        if not os.path.exists(outDir):
            os.makedirs(outDir)

        # clean up trailing slashes (will be re-added later)
        self.outDir = outDir.rstrip('/')
        self.classes: List[PyClass] = []
        self.files: List[PGFile] = self._parser.transform()

        for file in self.files:  # sift through the files and find any suspect type declarations.
            declarations, types = set(), set()
            for item in file.types:
                types.add(item[0])
            # Fill the set before re-iterating against delcarations.
            for item in file.declarations:
                declarations.add(file.declarations[item][0])

            for item in declarations:
                if item not in types and item not in ACCEPTED_TYPES:
                    raise ValueError(
                        f"The declaration of type {item} was specified but no type {item} exists.")

        del(self._parser)  # save memory, the parser is dense and repetitive


class NodeJSCompiler(Compiler):

    def __init__(self, inFiles: List[str], outDir: str, verbose: bool = False):
        super().__init__(inFiles, outDir, verbose)

    def compile(self):
        import shutil
        shutil.copyfile(os.path.join(os.path.dirname(__file__),
                                     'node_library/protogen.js'), self.outDir+'/protogen.js')
        shutil.copyfile(os.path.join(os.path.dirname(__file__),
                                     'node_library/README.md'), self.outDir+'/README.md')

        print(
            'Notice: Support for submessages in NodeJS output is only partially supported.')

        for item in self.files:
            print('Compiling {} into {}/{}_proto.js'
                  ''.format(item.filename, self.outDir, item.header))
            file = open(self.outDir + '/' + item.header + '_proto.js', 'w')
            self.generateCode(out=file, file=item)
            file.write(os.linesep)
            file.close()

    def generateCode(self, out: TextIOWrapper, file: PGFile):
        out.write("const { Message } = require('./protogen')\n"
                  "const { decode } = require('messagepack')\n")

        for item in file.classes:
            self.printClass(out, file, item, 0, True)
        out.write("\n")
        self.printFactory(out, file)
        self.printExports(out, file)

    def printClass(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass,
                   indent: int, root: bool):
        if root:
            out.write(f"\nclass {pyClass.name} extends Message {{\n")
        else:
            out.write(f"\n{tab*indent}class {pyClass.name} {{\n")

        out.write(f"\n{tab*(indent+1)}constructor(data = null) {{\n")
        out.write(f"{tab*(indent+2)}super()\n")

        if root:
            self.printData(out, file, pyClass, indent+2)
        out.write(f'{tab*(indent+1)}}}\n')
        self.printMethods(out, file, pyClass, indent+1)
        out.write("}\n")

    def printData(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int):
        out.write(f"{tab*indent}if (data != null) {{\n")
        out.write(f"{tab*(indent+1)}this.data = {{\n")

        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                # variable type, required/optional
                v_type, req = file.declarations[item]
                short = util.inferShortName(item)
                if v_type in ACCEPTED_TYPES:
                    out.write(
                        f'{tab*(indent+2)}{short}: [data[\'{short}\'], {str(req).lower()}, false], // {v_type} \n')
                else:
                    out.write(
                        f'{tab*(indent+2)}{short}: [new {v_type}(data[\'{short}\']), {str(req).lower()}, true], // {v_type}\n')
        out.write(f"{tab*(indent+1)}}}\n")
        out.write(f"{tab*indent}}} else {{\n")
        out.write(f"{tab*(indent+1)}this.data = {{\n")
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                v_type, req = file.declarations[item]
                short = util.inferShortName(item)
                # primitive data type
                if v_type == 'list':
                    out.write(
                        f'{tab*(indent+2)}{ short}: [[], {str(req).lower()}, false], // {v_type} \n')
                elif v_type == 'map':
                    out.write(
                        f'{tab*(indent+2)}{short}: [{{}}, {str(req).lower()}, false], // {v_type} \n')
                elif v_type in ACCEPTED_TYPES:
                    out.write(
                        f'{tab*(indent+2)}{short}: [null, {str(req).lower()}, false], // {v_type} \n')
                else:
                    out.write(
                        f'{tab*(indent+2)}{short}: [new {v_type}(), {str(req).lower()}, true], // {v_type}\n')
        out.write(f"{tab*(indent+1)}}}\n{tab*indent}}}\n")

    def printMethods(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int):
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                v_type, req = file.declarations[item]
                short = util.inferShortName(item)

                # Get methods
                self.printArgs(out, file, pyClass, indent, item, 'get')
                out.write(f'{tab*indent}get_{short}() {{\n')
                out.write(
                    f'{tab*(indent+1)}return this.data.{short}[0] // {v_type}\n')
                out.write(f'{tab*indent}}}\n\n')

                # Set methods
                self.printArgs(out, file, pyClass, indent, item, 'set')
                if v_type in JS_TYPES:
                    out.write(
                        f'{tab*indent}set_{short}({short}) {{ // {JS_TYPES[v_type]}\n')
                    out.write(
                        f'{tab*(indent+1)}this._assertType("{short}", {short}, "{JS_TYPES[v_type]}", "{v_type}")\n')
                    # out.write('{}if (typeof {} != "{}") throw new TypeError("{} should be of type {}")\n'.format(
                    #     (tab*(indent+1)), short, JS_TYPES[v_type], short, JS_TYPES[v_type]))
                else:
                    out.write(
                        f'{tab*indent}set_{short}({short}) {{ // {v_type}\n')
                out.write(f'{tab*(indent+1)}this.data.{short}[0] = {short}\n')
                out.write(f'{tab*(indent+1)}return this\n{tab*indent}}}\n')

    def printArgs(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int, file_item, set_get: str):
        if util.inferParentClass(file_item) == pyClass.fqname:
            thing = file.declarations[file_item]
            short = util.inferShortName(file_item)
            v_type = JS_TYPES.get(thing[0], thing[0])
            out.write(f'{tab*indent}/**\n')
            if set_get == 'set':
                short = util.inferShortName(file_item)
                out.write(f'{tab*indent} * @param {{ {v_type} }} {short}\n')
            elif set_get == 'get':
                out.write(
                    f'{tab*indent} * @returns {{ {v_type} }}\n')
            out.write(f'{tab*indent} */\n')

    def printFactory(self, out: TextIOWrapper, file: PGFile, indent: int = 0):
        out.write(f"class {file.header}Factory {{\n"
                  f"{tab*(indent+1)}static deserialize(data) {{\n"
                  f"{tab*(indent+2)}data = decode(data)\n"
                  f"{tab*(indent+2)}if (Object.keys(data).length > 1) {{ throw "
                  f"TypeError('This is likely not a Protogen packet.') }}\n"
                  f"{tab*(indent+2)}var packetType = Object.keys(data)[0]\n")
        for pyClass in file.classes:
            out.write(
                f"{tab*(indent+2)}if (packetType == '{pyClass.name}') {{ return new {pyClass.name}(data[packetType]) }}\n")
        out.write(
            f"{tab*(indent+2)}else {{ throw TypeError('No appropriate class found.') }}\n")
        out.write(f"{tab}}}\n}}\n\n")

    def printExports(self, out: TextIOWrapper, file: PGFile):
        out.write(
            f'module.exports.{file.header}Factory = {file.header}Factory\n')
        for item in file.classes:
            out.write(f'module.exports.{item.fqname} = {item.name}\n')


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
                if type in ACCEPTED_TYPES:
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
        out.write("from protogen.library.message import Serializable\n"),
        out.write("from protogen.library.message import Printable\n\n")
        for item in file.classes:
            if item.parent is None:
                self.printClass(out, file, item, 0, True)
        self.printFactory(out, file)
