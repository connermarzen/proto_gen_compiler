import os
from io import TextIOWrapper
from typing import List

import protogen.util as util
from protogen.compiler import Compiler
from protogen.compiler import tab as tab
from protogen.library.python.std import ACCEPTED_TYPES, JS_TYPES
from protogen.util import PGFile, PyClass


class NodeJSCompiler(Compiler):

    def __init__(self, inFiles: List[str], outDir: str, verbose: bool = False):
        super().__init__(inFiles, outDir, verbose)

    def compile(self):
        import shutil
        shutil.copyfile(os.path.join(os.path.dirname(__file__),
                                     'protogen.js'), self.outDir+'/protogen.js')
        shutil.copyfile(os.path.join(os.path.dirname(__file__),
                                     'README.md'), self.outDir+'/README.md')

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
