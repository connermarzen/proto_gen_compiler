from typing import Dict
from pprint import pprint
import msgpack


class ValidationError(Exception):
    def __init__(self, var_name):
        super().__init__("{} is marked as required, yet is missing its value.".format(var_name))


class Serializable(object):
    @staticmethod
    def deserialize(data: bytes) -> Dict:
        return msgpack.unpackb(data, raw=False)

    def serialize(self):
        return msgpack.packb({self.__class__.__name__: self._build_data_dict()})

    def _build_data_dict(self, output=None, data=None):
        if data is None:
            data = self.data
            output = {}
        for item in data:
            if data[item][2]:
                output[item] = {}
                self._build_data_dict(output[item], data[item][0].data)
            else:
                # if data[item][1] and not data[item][0]:
                #     raise ValidationError(item)
                output[item] = data[item][0]
        return output

    def _assertType(self, name: str, value, datatype: object, canon_type: str):
        if type(value) is not datatype:
            raise ValueError(
                f"Attribute {name} is not of the proper type: {datatype.__name__}.")
        elif canon_type == 'uint32':
            if value > 2 ** 32 - 1 or value < 0:
                raise ValueError(
                    f"Attribute {name} is cannonically type {canon_type} and should be within 0 and 4294967295.")
            if value % 1 != 0:
                raise ValueError(
                    f"Attribute {name} is cannonically type {canon_type} and should not be a floating point number.")
        elif canon_type == 'int':
            if value > (2 ** 31) - 1 or value < -(2 ** 31):
                raise ValueError(
                    f"Attribute {name} is cannonically type {canon_type} and should be within ${-1 * 2 ** 31} and ${2 ** 31 - 1}.")
            if value % 1 != 0:
                raise ValueError(
                    f"Attribute {name} is cannonically type {canon_type} and should not be a floating point number.")
        else:
            return


class Printable(object):
    def __str__(self) -> str:
        return self._str()

    def _req(self, data):
        return 'req' if data[1] else 'opt'

    def _str(self, data=None, indent=0):
        tab = '    '
        output = ''
        if data is None:
            data = self.data
        for item in data:
            if data[item][2]:
                output += "{}{} ({}): \n{}".format(tab*indent, item,
                                                   self._req(data[item]), self._str(data[item][0].data, indent+1))
            else:
                output += "{}{} ({}): {}\n".format(tab*indent,
                                                   item, self._req(data[item]), data[item][0])
        return output
