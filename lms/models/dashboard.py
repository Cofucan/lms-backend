from tortoise import fields
from models.base import BaseModel


class Notification(BaseModel):
    message = fields.CharField(max_length=255, null=True)
    sender = fields.ForeignKeyField(
        "models.User", related_name="notifications", null=True
    )


class Announcement(BaseModel):
    title = fields.CharField(max_length=128, null=True)
    content = fields.CharField(max_length=655, null=True)
    creator = fields.ForeignKeyField(
        "models.User", related_name="announcements", null=True
    )
    general = fields.BooleanField(default=False)
    stack = fields.CharField(max_length=55, null=True)
    track = fields.CharField(max_length=55, null=True)
    proficiency = fields.CharField(max_length=100, null=True)
    stage = fields.IntField(null=True)


class Lesson(BaseModel):
    title = fields.CharField(max_length=128, null=True)
    content = fields.CharField(max_length=655, null=True)
    stack = fields.CharField(max_length=55, null=True)
    track = fields.CharField(max_length=55, null=True)
    proficiency = fields.CharField(max_length=55, null=True)
    stage = fields.IntField(null=True)
    creator = fields.ForeignKeyField(
        "models.User", related_name="lessons", null=True
    )
    media = fields.ForeignKeyField(
        "models.Media", related_name="lessons", null=True
    )


class Quiz(BaseModel):
    lesson = fields.ForeignKeyField(
        "models.Lesson", related_name="quizes", null=True
    )
    user = fields.ForeignKeyField(
        "models.User", related_name="quizes", null=True
    )
    content = fields.CharField(max_length=655, null=True)
    deadline = fields.DatetimeField(auto_now=False, null=True)
    score = fields.FloatField(default=0.0, null=True)


class PromotionTask(BaseModel):
    title = fields.CharField(max_length=128, null=True)
    content = fields.CharField(max_length=655, null=True)
    stack = fields.CharField(max_length=55, null=True)
    track = fields.CharField(max_length=55, null=True)
    proficiency = fields.CharField(max_length=55, null=True)
    stage = fields.IntField(null=True)
    feedback = fields.CharField(max_length=256, null=True)
    active = fields.BooleanField(default=False)
    deadline = fields.DatetimeField(auto_now=False, null=True)
    creator = fields.ForeignKeyField(
        "models.User", related_name="promotion-tasks", null=True
    )


class TaskSubmission(BaseModel):
    user = fields.ForeignKeyField(
        "models.User", related_name="submissions", null=True
    )
    task = fields.ForeignKeyField(
        "models.PromotionTask", related_name="submissions", null=True
    )
    url = fields.CharField(max_length=500, null=True)
    graded = fields.BooleanField(default=False)
    passed = fields.BooleanField(default=False)
    submitted = fields.BooleanField(default=False)


class Resource(BaseModel):
    """Resources"""

    title = fields.CharField(max_length=128, null=True)
    content = fields.CharField(max_length=655, null=True)
    stack = fields.CharField(max_length=55, null=True)
    track = fields.CharField(max_length=55, null=True)
    proficiency = fields.CharField(max_length=55, null=True)
    stage = fields.IntField(null=True)
    creator = fields.ForeignKeyField(
        "models.User", related_name="resources", null=True
    )
    media = fields.ForeignKeyField(
        "models.Media", related_name="resources", null=True
    )


class Media(BaseModel):
    """Media contents

    Fields (All charfields):
        title, url, filename, and filesize
    """

    title = fields.CharField(max_length=128, null=True)
    url = fields.CharField(max_length=500, null=True)
    filename = fields.CharField(max_length=200, null=True)
    filesize = fields.CharField(max_length=100, null=True)
