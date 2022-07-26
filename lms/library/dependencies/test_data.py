from essential_generators import DocumentGenerator
import random

gen = DocumentGenerator()

stack = [
    "backend",
    "frontend",
    "design",
    "product management",
    "cloud engineering",
    "data science",
    "mobile development",
    "digital marketing",
]
track = [
    "nodejs",
    "python",
    "php",
    "golang",
    "vuejs",
    "reactjs",
    "vanillajs",
    "product design",
    "graphic design",
]
proficiency = ["beginner", "intermediate", "advanced"]
stage = random.randint(0, 10)


def generate_user():
    template_user = {
        "first_name": "name",
        "surname": "name",
        "email": "email",
        "password": "bill#oJworl765d",
    }
    gen.set_template(template_user)
    return gen.document()


def generate_announcement(general: bool):
    template = {
        "title": "name",
        "content": "sentence",
        "stack": stack,
        "track": track,
        "proficiency": proficiency,
        "stage": stage,
        "general": "false",
    }
    if general:
        template_general = {
            "title": "name",
            "content": "sentence",
            "general": "true",
        }
        gen.set_template(template_general)
    else:
        gen.set_template(template)
    return gen.document()


def generate_lesson():
    template = {
        "title": "sentence",
        "content": "paragraph",
        "stack": stack,
        "track": track,
        "proficiency": proficiency,
        "stage": stage,
    }
    gen.set_template(template)
    return gen.document()


def generate_task():
    template = {
        "title": "sentence",
        "content": "paragraph",
        "stack": stack,
        "track": track,
        "proficiency": proficiency,
        "stage": stage,
        "feedback": "sentence",
        "active": "true",
        "deadline": random.randint(1, 14),
    }
    gen.set_template(template)
    return gen.document()
