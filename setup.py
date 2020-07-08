from setuptools import find_packages, setup

setup(
    name="protogen",
    version="1.0",
    description="Protocol Generator for Python",
    author="Conner Marzen",
    author_email="connermarzen@gmail.com",
    url="https://github.com/connermarzen/proto_gen_compiler",
    packages=find_packages(),
    install_requires=['lark-parser', 'msgpack-python']
)
