const { encode, decode } = require('messagepack')

class ValidationError extends Error {
    constructor(message) {
        super(message)
        this.name = "ValidationError"
    }
}

function validate(data) {
    for (const [key, value] of Object.entries(data)) {
        if (typeof value[0] === "object") {
            this.validate(value)
        }
        else {
            if (value[0] == null && value[1]) {
                throw ValidationError(`${key} is missing a value and is marked as required.`)
            }
        }
    }
}

class Serializable {
    serialize() {
        validate(this.data)
        return encode({ [this.constructor.name]: this.data })
    }
}

module.exports.Serializable = Serializable