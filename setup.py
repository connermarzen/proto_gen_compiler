from distutils.core import setup
from setuptools import find_packages

setup(
    name="proto_gen_compiler",
    version="1.0",
    description="Protocol Generator for Python",
    author="Conner Marzen",
    url="https://github.com/connermarzen/proto_gen_compiler",
    packages=find_packages(),
    requires=['lark-parser']
)
