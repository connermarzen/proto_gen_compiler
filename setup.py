from setuptools import find_packages, setup

setup(
    name="protogen",
    version="1.1.0-beta-1",
    description="Protocol Generator for Python",
    author="Conner Marzen",
    author_email="connermarzen@gmail.com",
    url="https://github.com/connermarzen/protogen",
    packages=find_packages(),
    install_requires=['lark-parser', 'msgpack-python'],
    include_package_data=True
)
