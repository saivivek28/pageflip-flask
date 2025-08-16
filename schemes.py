from marshmallow import fields, Schema, validates, ValidationError
from marshmallow.validate import Length
import re

class User_schema(Schema):
    name = fields.Str(required=False)
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=Length(min=6, error="Password must be at least 6 characters long.")
    )

    
