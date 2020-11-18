import os
from io import TextIOWrapper
from typing import List

import protogen.util as util
from protogen.core import PGParser
from protogen.library.std import ACCEPTED_TYPES, JS_TYPES, PYTHON_TYPES
from protogen.util import PGFile, PyClass


class NodeJSCompiler(object):

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

    def compile(self):
        import shutil

        shutil.copyfile(os.path.join(os.path.dirname(__file__),
                                     'node_library/protogen.js'), self.outDir+'/protogen.js')
        shutil.copyfile(os.path.join(os.path.dirname(__file__),
                                     'node_library/README.md'), self.outDir+'/README.md')

        for item in self.files:
            print(
                'Notice: Support for submessages in NodeJS output is only partially supported.')
            print(
                'Notice: Type checking is not supported, so make sure you adhere to your protocol!')
            print('View the generated README.md for more information.\n')
            print('Compiling {} into {}/{}_proto.js'
                  ''.format(item.filename, self.outDir, item.header))
            file = open(self.outDir + '/' + item.header + '_proto.js', 'w')
            self.generateCode(out=file, file=item)
            file.write(os.linesep)
            file.close()

    def printData(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int):
        tab = '    '

        out.write("{}if (data != null) {{\n".format(tab*indent))
        out.write("{}this.data = {{\n".format(tab*(indent+1)))
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                thing = file.declarations[item]
                short = util.inferShortName(item)
                if thing[0] in ACCEPTED_TYPES:
                    out.write('{}{}: [data[\'{}\'], {}, false], // {} \n'.format(
                        tab*(indent+2), short, short, str(thing[1]).lower(), thing[0]))
                else:
                    out.write('{}{}: [new {}(data[\'{}\']), {}, true], // {}\n'.format(
                        tab*(indent+2), short, thing[0], short, str(thing[1]).lower(), thing[0]))
        out.write("{}}}\n".format(tab*(indent+1)))
        out.write("{}}} else {{\n".format(tab*indent))

        out.write("{}this.data = {{\n".format(tab*(indent+1)))
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                thing = file.declarations[item]
                short = util.inferShortName(item)
                # primitive data type
                if thing[0] == 'list':
                    out.write('{}{}: [[], {}, false], // {} \n'.format(
                        tab*(indent+2), short, str(thing[1]).lower(), thing[0]))
                elif thing[0] == 'map':
                    out.write('{}{}: [{{}}, {}, false], // {} \n'.format(
                        tab*(indent+2), short, str(thing[1]).lower(), thing[0]))
                elif thing[0] in ACCEPTED_TYPES:
                    out.write('{}{}: [null, {}, false], // {} \n'.format(
                        tab*(indent+2), short, str(thing[1]).lower(), thing[0]))
                else:
                    out.write('{}{}: [new {}(), {}, true], // {}\n'.format(
                        tab*(indent+2), short, thing[0], str(thing[1]).lower(), thing[0]))
        out.write("{}}}\n".format(tab*(indent+1)))
        out.write("{}}}\n".format(tab*indent))
        

    def printArgs(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int, file_item, set_get: str):
        tab = '    '
        if util.inferParentClass(file_item) == pyClass.fqname:
            thing = file.declarations[file_item]
            short = util.inferShortName(file_item)
            var_type = JS_TYPES.get(thing[0], thing[0])
            if set_get == 'set':
                out.write('{}/**\n'.format(tab*indent))
                short = util.inferShortName(file_item)
                out.write('{} * @param {{ {} }} {}\n'.format(tab *
                                                             indent, var_type, short))
                out.write('{} */\n'.format(tab*indent))
            elif set_get == 'get':
                out.write('{}/**\n'.format(tab*indent))
                out.write(
                    '{} * @returns {{ {} }}\n'.format(tab * indent, var_type))
                out.write('{} */\n'.format(tab*indent))

    def printMethods(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int):
        tab = '    '
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                thing = file.declarations[item]
                short = util.inferShortName(item)

                # Get methods
                self.printArgs(out, file, pyClass, indent, item, 'get')
                out.write('{}get_{}() {{\n'.format(
                    (tab*indent), short, thing[0]))

                out.write('{}return this.data.{}[0] // {}\n'.format(
                    (tab*(indent+1)), short, thing[0]))

                out.write('{}}}\n\n'.format(tab*indent))

                # Set methods
                self.printArgs(out, file, pyClass, indent, item, 'set')
                if thing[0] in JS_TYPES:
                    out.write('{}set_{}({}) {{ // {}\n'.format(
                        (tab*indent), short, short, JS_TYPES[thing[0]]))
                    out.write('{}this._assertType("{}", {}, "{}", "{}")\n'.format(
                        tab*(indent+1), short, short, JS_TYPES[thing[0]], thing[0]))
                    # out.write('{}if (typeof {} != "{}") throw new TypeError("{} should be of type {}")\n'.format(
                    #     (tab*(indent+1)), short, JS_TYPES[thing[0]], short, JS_TYPES[thing[0]]))
                else:
                    out.write('{}set_{}({}) {{ // {}\n'.format(
                        (tab*indent), short, short, thing[0]))
                out.write('{}this.data.{}[0] = {}\n'.format(
                    (tab*(indent+1)), short, short))
                out.write('{}return this\n'.format((tab*(indent+1))))
                out.write('{}}}\n'.format(tab*indent))

    def printFactory(self, out: TextIOWrapper, file: PGFile):
        tab = '    '
        indent = 0
        out.write("class {}Factory {{\n".format(file.header))
        out.write("{}static deserialize(data) {{\n".format(tab*(indent+1)))
        out.write("{}data = decode(data)\n".format(tab*(indent+2)))
        out.write("{}if (Object.keys(data).length > 1) {{ throw "
                  "TypeError('This is likely not a Protogen packet.') }}\n".format(tab*(indent+2)))
        out.write(
            "{}var packetType = Object.keys(data)[0]\n".format(tab*(indent+2)))
        for pyClass in file.classes:
            out.write("{}if (packetType == '{}') {{ return new {}(data[packetType]) }}\n".format(
                tab*(indent+2), pyClass.name, pyClass.name))
        out.write("{}else {{ throw TypeError('No appropriate class found.') }}\n".format(
            tab*(indent+2)))
        out.write("{}}}\n".format("    "))
        out.write("{}}}\n".format(""))

    def printClass(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass,
                   indent: int, root: bool):
        tab = '    '
        if root:
            out.write("\nclass {} extends Message {{\n".format(pyClass.name))
        else:
            out.write("\n{}class {} {{\n".format(
                tab*indent, pyClass.name))
        out.write("\n{}constructor(data = null) {{\n"
                  .format(tab*(indent+1)))
        out.write("{}super()\n"
                  .format(tab*(indent+2)))
        if root:
            # out.write("{}if (data) {{\n".format(tab*(indent+2)))
            # out.write("{}this.data = data\n".format(tab*(indent+3)))
            # out.write("{}}}\n".format(tab*(indent+2)))
            # out.write("{}else {{\n".format(tab*(indent+2)))
            # self.printData(out, file, pyClass, indent+3)
            # out.write("{}}}\n".format(tab*(indent+2)))
            self.printData(out, file, pyClass, indent+2)
        out.write('{}}}\n'.format(tab*(indent+1)))
        self.printMethods(out, file, pyClass, indent+1)

        out.write("}\n")

    def printExports(self, out: TextIOWrapper, file: PGFile):
        out.write(
            'module.exports.{0}Factory = {0}Factory\n'.format(file.header))
        for item in file.classes:
            out.write('module.exports.{} = {}\n'.format(
                item.fqname, item.name))

    def generateCode(self, out: TextIOWrapper, file: PGFile):
        out.write("const { Message } = require('./protogen')\n")
        out.write("const { decode } = require('messagepack')\n")

        for item in file.classes:
            self.printClass(out, file, item, 0, True)
        out.write("\n")
        self.printFactory(out, file)
        out.write("\n")
        self.printExports(out, file)


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
            out.write("\nclass {}(Serializable, "
                      "Printable):\n".format(pyClass.name))
        else:
            out.write("\n{}class {}(Serializable, Printable):\n".format(
                tab*indent, pyClass.name))
        out.write("\n{}def __init__(self, data: dict = None):\n"
                  .format(tab*(indent+1)))
        self.printAttributes(out, file, pyClass, indent+1)
        out.write("\n{}if data is not None:\n".format(tab*(indent+2)))
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                short = util.inferShortName(item)
                type, required = file.declarations[item]
                if type in ACCEPTED_TYPES:
                    out.write("{}self.data['{}'][0] = data['{}']\n".format(
                        tab*(indent+3), short, short))
                # local, nested class (needs 'self')
                elif type in pyClass.gatherSubclasses('name'):
                    out.write("{}self.data['{}'][0] = self.{}(data['{}'])\n".format(
                        tab*(indent+3), short, type, short))
                # local, non-nested class (doesn't need 'self')
                else:
                    out.write("{}self.data['{}'][0] = {}(data['{}'])\n".format(
                        tab*(indent+3), short, type, short))

        for item in pyClass.subclasses:
            self.printClass(out, file, item, indent+1, False)

        self.printMethods(out, file, pyClass, indent+1)
        out.write("{}# End Class {}\n".format(tab*indent, pyClass.name))

    def printAttributes(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int):
        tab = '    '
        out.write('{}self.data = {{\n'.format(tab*(indent+1)))
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                # type, required = file.declarations[item][0], file.declarations[item][1]
                type, required = file.declarations[item]
                short = util.inferShortName(item)
                # primitive data type
                if type == 'list':
                    out.write('{}\'{}\': [[], {}, False],\n'.format(
                        tab*(indent+2), short, required))
                elif type == 'map':
                    out.write('{}\'{}\': [{{}}, {}, False],\n'.format(
                        tab*(indent+2), short, required))
                elif type in ACCEPTED_TYPES:
                    out.write('{}\'{}\': [None, {}, False],\n'.format(
                        tab*(indent+2), short, required))
                # local, nested class (needs 'self')
                elif type in pyClass.gatherSubclasses('name'):
                    out.write('{}\'{}\': [self.{}(), {}, True],\n'.format(
                        tab*(indent+2), short, type, required))
                # local, non-nested class (doesn't need 'self')
                else:
                    out.write('{}\'{}\': [{}(), {}, True],\n'.format(
                        tab*(indent+2), short, type, required))

        out.write('{}}}\n'.format(tab*(indent+1)))

    def printMethods(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, indent: int):
        tab = '    '
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                thing = file.declarations[item]
                short = util.inferShortName(item)

                # Get methods
                if thing[0] in ACCEPTED_TYPES:
                    out.write('\n{}def get_{}(self) -> {}:\n'.format(
                        (tab*indent), short, PYTHON_TYPES[thing[0]]))
                else:
                    out.write('\n{}def get_{}(self) -> {}:\n'.format(
                        (tab*indent), short, thing[0]))
                out.write('{}return self.data[\'{}\'][0]\n'.format(
                    (tab*(indent+1)), short))

                # Set methods
                if thing[0] in PYTHON_TYPES:
                    out.write('\n{}def set_{}(self, {}: {}) -> \'{}\':\n'.format(
                        (tab*indent), short,
                        short, PYTHON_TYPES[thing[0]], pyClass.name))
                    out.write('{}self._assertType("{}", {}, {}, "{}")\n'.format(
                        (tab*(indent+1)), short, short, PYTHON_TYPES[thing[0]], thing[0]))
                else:
                    out.write('\n{}def set_{}(self, {}: {}) -> \'{}\':\n'.format(
                        (tab*indent), short,
                        short, thing[0], pyClass.name))
                out.write('{}self.data[\'{}\'][0] = {}\n'.format(
                    (tab*(indent+1)), short, short))
                out.write('{}return self\n'.format((tab*(indent+1))))

    def printFactory(self, out: TextIOWrapper, file: PGFile):
        tab = '    '
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
                out.write('{}if packetType == \'{}\':\n'.format(
                    tab*3, item.name))
                out.write('{}return {}(data[item])\n'.format(tab*4, item.name))
        outString = (
            "            else:\n"
            "                raise AttributeError('Respective class not found.')\n"
        )
        out.write(outString)

    def generateCode(self, out: TextIOWrapper, file: PGFile, indent: str = '    '):
        out.write("from protogen.library.message import Serializable\n"),
        out.write("from protogen.library.message import Printable\n\n")
        for item in file.classes:
            if item.parent is None:
                self.printClass(out, file, item, 0, True)
        self.printFactory(out, file)
