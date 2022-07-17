from tortoise import fields
from models.base import BaseModel


class Notification(BaseModel):
    message = fields.CharField(max_length=255, null=True)
    sender = fields.ForeignKeyField(
        "models.User", related_name="notifications", null=True
    )


class Announcement(BaseModel):
    title = fields.CharField(max_length=255, null=True)
    content = fields.CharField(max_length=655, null=True)
    creator = fields.ForeignKeyField(
        "models.User", related_name="announcements", null=True
    )
    general = fields.BooleanField(default=False)
    stack = fields.CharField(max_length=100, null=True)
    track = fields.CharField(max_length=255, null=True)
    proficiency = fields.CharField(max_length=100, null=True)
    stage = fields.IntField(null=True)


class Stage(BaseModel):
    stage = fields.IntField(null=True)
    lesson = fields.ForeignKeyField(
        "models.Lesson", related_name="stages", null=True
    )


class Lesson(BaseModel):
    title = fields.CharField(max_length=255, null=True)
    stack = fields.CharField(max_length=100, null=True)
    track = fields.CharField(max_length=255, null=True)
    proficiency = fields.CharField(max_length=100, null=True)
    stage = fields.IntField(null=True)
    creator = fields.ForeignKeyField(
        "models.User", related_name="lessons", null=True
    )
    content = fields.CharField(max_length=655, null=True)


class Quiz(BaseModel):
    stage = fields.ForeignKeyField(
        "models.Stage", related_name="quizes", null=True
    )
    user = fields.ForeignKeyField(
        "models.User", related_name="quizes", null=True
    )
    content = fields.CharField(max_length=655, null=True)
    deadline = fields.DatetimeField(auto_now=False, null=True)


class PromotionTask(BaseModel):
    title = fields.CharField(max_length=255, null=True)
    content = fields.CharField(max_length=655, null=True)
    stack = fields.CharField(max_length=100, null=True)
    track = fields.CharField(max_length=255, null=True)
    proficiency = fields.CharField(max_length=100, null=True)
    stage = fields.IntField(null=True)
    feedback = fields.CharField(max_length=655, null=True)
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

    title = fields.CharField(max_length=255, null=True)
    creator = fields.ForeignKeyField(
        "models.User", related_name="resources", null=True
    )
    content = fields.CharField(max_length=655, null=True)
    url = fields.CharField(max_length=500, null=True)
    filename = fields.CharField(max_length=200, null=True)
    filesize = fields.CharField(max_length=100, null=True)


class Media(BaseModel):
    """Media contents"""

    content = fields.ForeignKeyField(
        "models.Lesson", related_name="media", null=True
    )
    url = fields.CharField(max_length=500, null=True)
    filename = fields.CharField(max_length=200, null=True)
    filesize = fields.CharField(max_length=100, null=True)
