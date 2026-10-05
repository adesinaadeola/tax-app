from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Str(dump_only=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class DefaultAllowDeductSchema(Schema):
    id = fields.Str(dump_only=True)
    amount = fields.Float()
    description = fields.Str()
    payperiod = fields.Int()
    taxable = fields.Str()   

class AllowDeductCreationSchema(DefaultAllowDeductSchema):
    amount = fields.Float(required=True)    
    description = fields.Str(required=True)
    payperiod = fields.Int(required=True)
    userid = fields.Int(required=True)
    taxable = fields.Str(required=True)

class UpdateAllowDeductSchema(DefaultAllowDeductSchema):
    userid = fields.Int(required=True)

class DefaultReliefSchema(Schema):
    id = fields.Str(dump_only=True)
    amount = fields.Float()
    description = fields.Str()
    payperiod = fields.Int()

class ReliefCreationSchema(DefaultAllowDeductSchema):
    amount = fields.Float(required=True)    
    description = fields.Str(required=True)
    payperiod = fields.Int(required=True)
    userid = fields.Int(required=True)