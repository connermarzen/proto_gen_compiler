const { encode, decode } = require('messagepack')

class ValidationError extends Error {
    constructor(message) {
        super(message)
        this.name = "ValidationError"
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
}

module.exports.Message = Message