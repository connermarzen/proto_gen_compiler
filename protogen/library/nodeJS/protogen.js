const { encode, decode } = require('messagepack')

class ValidationError extends Error {
    constructor(message) {
        super(message)
        this.name = "ValidationError"
    }
}

class ValueError extends Error {
    constructor(message) {
        super(message)
        this.name = "ValueError"
    }
}

class Message {
    static deserialize(data) {
        return decode(data)
    }

    serialize() {
        return encode({ [this.constructor.name]: this._build_data_dict() })
    }

    _build_data_dict(output = null, data = null) {
        if (data == null) {
            data = this.data
            output = {}
        }
        for (const [key, value] of Object.entries(data)) {
            if (value[2] == true) {
                output[key] = {}
                this._build_data_dict(output[key], value[0].data)
            } else {
                output[key] = value[0]
            }
        }
        return output
    }

    _toString(data = null, indent = 0) {
        const tab = '    '
        var output = ''
        if (data == null) {
            data = this.data
        }
        for (const [key, value] of Object.entries(data)) {
            if (value[2] == true) {
                output += `${tab.repeat(indent)}${key} (${value[1] ? 'req' : 'opt'}): \n${this._toString(value[0].data, indent + 1)}`
            } else {
                output += `${tab.repeat(indent)}${key} (${value[1] ? 'req' : 'opt'}): ${value[0]}\n`
            }
        }
        return output
    }

    toString() {
        return this._toString()
    }

    _assertType(name, value, type, canon_type) {
        if (type == 'Array' && Array.isArray(value)) {
            return
        }
        else if (value.constructor == Object) {
            return
        }
        else if (typeof value != type) {
            throw new TypeError(`Attribute ${name} is not of the proper type: ${type}.`)
        }
        else if (canon_type == 'int') {
            if (value > (2 ** 31) - 1 || value < -(2 ** 31)) {
                throw new ValueError(`Attribute ${name} is cannonically type ${canon_type} and should be within ${-1 * 2 ** 31} and ${2 ** 31 - 1}.`)
            }
            if (value % 1 !== 0) {
                throw new ValueError(`Attribute ${name} is cannonically type ${canon_type} and should not be a floating point number.`)
            }
        } else if (canon_type == 'uint32') {
            if (value > 2 ** 32 - 1 || value < 0) {
                throw new ValueError(`Attribute ${name} is cannonically type ${canon_type} and should be within 0 and 4294967295.`)
            }
            if (value % 1 !== 0) {
                throw new ValueError(`Attribute ${name} is cannonically type ${canon_type} and should not be a floating point number.`)
            }
        }
        else return
    }
}

module.exports.Message = Message