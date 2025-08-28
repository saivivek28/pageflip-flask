from marshmallow import fields, Schema, validates, ValidationError, validates_schema
from marshmallow.validate import Length
import re

class User_schema(Schema):
    name = fields.Str(required=False)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    confirm_password = fields.Str(required=True)
    phone = fields.Int(required=True)
    @validates("password")
    def validate_password(self, data):
        if data[0].islower():
            return ValueError
        
    @validates("confirm_password")
    def validate_confirm_password(self, data):
        if data[0].islower():
            return ValueError
        
    @validates_schema
    def validates_passwords(self, data, *args):
        if not data["password"] == data["confirm_password"]:
            return  ValidationError
        
            
    
