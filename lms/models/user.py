from tortoise import fields
from models.base import BaseModel


class User(BaseModel):
    username = fields.CharField(max_length=50, null=True)
    first_name = fields.CharField(max_length=100, null=True)
    surname = fields.CharField(max_length=100, null=True)
    email = fields.CharField(max_length=100, null=True)
    phone = fields.CharField(max_length=100, null=True)
    gender = fields.CharField(max_length=100, null=True)
    stage = fields.IntField(null=True)
    stack = fields.CharField(max_length=100, null=True)
    track = fields.CharField(max_length=100, null=True)
    proficiency = fields.CharField(max_length=100, null=True)
    last_active = fields.DatetimeField(auto_now=True)
    is_admin = fields.BooleanField(default=False)
    hashed_password = fields.CharField(max_length=255, null=True)
    email_verified = fields.BooleanField(default=False)


class Picture(BaseModel):
    user = fields.ForeignKeyField(
        "models.User", related_name="picture", null=True
    )
    url = fields.CharField(max_length=500, null=True)
    filename = fields.CharField(max_length=200, null=True)
    filesize = fields.CharField(max_length=100, null=True)
