import os
from io import TextIOWrapper
from typing import List
import time

import protogen.util as util
from protogen.compiler import Compiler
from protogen.compiler import tab as tab
from protogen.library.python.std import ACCEPTED_TYPES, JS_TYPES
from protogen.util import PGFile, PyClass


class MarkdownCompiler(Compiler):
    def __init__(self, inFiles: List[str], outDir: str, verbose: bool = False):
        super().__init__(inFiles, outDir, verbose)

    def compile(self):
        import shutil
        shutil.copyfile(os.path.join(os.path.dirname(__file__),
                                     'standard_types.md'), self.outDir+'/standard_types.md')

        for item in self.files:
            print('Compiling {} into {}/{}.md'
                  ''.format(item.filename, self.outDir, item.header))
            file = open(self.outDir + '/' + item.header + '.md', 'w')
            self.generateCode(out=file, file=item)
            file.write(os.linesep)
            file.close()

        

    def generateCode(self, out: TextIOWrapper, file: PGFile):
        out.write(f"# {file.header} Documentation\n\n"
                  f"File: `{file.filename}`\n\n"
                  f"Created: {time.ctime()}\n\n")

        for item in file.classes:
            self.printClass(out, file, item, True)
        out.write("\n")
        # self.printFactory(out, file)
        # self.printExports(out, file)

    def printClass(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass, root: bool):
        out.write(f"## {pyClass.fqname}\n\n")

        self.printAttributes(out, file, pyClass)

    def printAttributes(self, out: TextIOWrapper, file: PGFile, pyClass: PyClass):
        for item in file.declarations:
            if util.inferParentClass(item) == pyClass.fqname:
                v_type, req = file.declarations[item]
                req = '**required**' if req else '*optional*'
                short = util.inferShortName(item)
                if v_type in ACCEPTED_TYPES:
                    out.write(f"* {short} &rightarrow; [`{v_type}`](./standard_types#{v_type}) {req}\n")
                else:
                    out.write(f"* {short} &rightarrow; [`{v_type}`](#{v_type}) {req}\n")
        out.write('\n')