from tortoise import fields
from models.base import BaseModel


class Notification(BaseModel):
    message = fields.CharField(max_length=255, null=True)
    sender = fields.ForeignKeyField(
        "models.User", related_name="notifications", null=True
    )


class Announcement(BaseModel):
    title = fields.CharField(max_length=255, null=True)
    message = fields.CharField(max_length=655, null=True)
    sender = fields.ForeignKeyField(
        "models.User", related_name="announcements", null=True
    )


class Stage(BaseModel):
    stage = fields.IntField(null=True)
    user = fields.ForeignKeyField(
        "models.User", related_name="stages", null=True
    )
    course = fields.ForeignKeyField(
        "models.Course", related_name="stages", null=True
    )


class Course(BaseModel):
    title = fields.CharField(max_length=255, null=True)
    track = fields.CharField(max_length=255, null=True)
    stage = fields.IntField(null=True)
    creator = fields.ForeignKeyField(
        "models.User", related_name="courses", null=True
    )
    content = fields.CharField(max_length=655, null=True)


class Quiz(BaseModel):
    course = fields.ForeignKeyField(
        "models.Course", related_name="quizes", null=True
    )
    stage = fields.ForeignKeyField(
        "models.Stage", related_name="quizes", null=True
    )
    user = fields.ForeignKeyField(
        "models.User", related_name="quizes", null=True
    )
    content = fields.CharField(max_length=655, null=True)
    deadline = fields.DatetimeField(auto_now=False, null=True)


class PromotionTask(BaseModel):
    course = fields.ForeignKeyField(
        "models.Course", related_name="tasks", null=True
    )
    stage = fields.ForeignKeyField(
        "models.Stage", related_name="tasks", null=True
    )
    user = fields.ForeignKeyField(
        "models.User", related_name="tasks", null=True
    )
    content = fields.CharField(max_length=655, null=True)
    deadline = fields.DatetimeField(auto_now=False, null=True)


class Resource(BaseModel):
    """Resources"""
    title = fields.CharField(max_length=255, null=True)
    sender = fields.ForeignKeyField(
        "models.User", related_name="resources", null=True
    )
    content = fields.CharField(max_length=655, null=True)
    url = fields.CharField(max_length=500, null=True)
    filename = fields.CharField(max_length=200, null=True)
    filesize = fields.CharField(max_length=100, null=True)


class Media(BaseModel):
    """Media contents"""

    content = fields.ForeignKeyField(
        "models.Course", related_name="media", null=True
    )
    url = fields.CharField(max_length=500, null=True)
    filename = fields.CharField(max_length=200, null=True)
    filesize = fields.CharField(max_length=100, null=True)