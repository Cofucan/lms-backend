from essential_generators import DocumentGenerator
import random

gen = DocumentGenerator()


def generate_user():
    template = {
        "first_name": "name",
        "surname": "name",
        "email": "email",
        "password": "bill#oJworl765d",
    }
    gen.set_template(template)
    return gen.document()


def generate_announcement(general: bool):
    template_user = {
        "title": "name",
        "content": "sentence",
        "stack": [
            "backend",
            "frontend",
            "design",
            "product management",
            "cloud engineering",
            "data science",
        ],
        "track": [
            "nodejs",
            "python",
            "php",
            "golang",
            "vuejs",
            "reactjs",
            "vanillajs",
            "product design",
            "ui/ux design",
        ],
        "proficiency": ["beginner", "intermediate", "advanced"],
        "stage": random.randint(1, 20),
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
        gen.set_template(template_user)
    return gen.document()


def generate_lesson():
    template = {
        "title": "sentence",
        "content": "paragraph",
        "stack": [
            "backend",
            "frontend",
            "design",
            "product management",
            "cloud engineering",
            "data science",
        ],
        "track": [
            "nodejs",
            "python",
            "php",
            "golang",
            "vuejs",
            "reactjs",
            "vanillajs",
            "product design",
            "ui/ux design",
        ],
        "proficiency": ["beginner", "intermediate", "advanced"],
        "stage": random.randint(1, 20),
    }
    gen.set_template(template)
    return gen.document()


def generate_task():
    template = {
        "title": "sentence",
        "content": "paragraph",
        "stack": [
            "backend",
            "frontend",
            "design",
            "product management",
            "cloud engineering",
            "data science",
        ],
        "track": [
            "nodejs",
            "python",
            "php",
            "golang",
            "vuejs",
            "reactjs",
            "vanillajs",
            "product design",
            "ui/ux design",
        ],
        "proficiency": ["beginner", "intermediate", "advanced"],
        "stage": random.randint(1, 20),
        "feedback": "sentence",
        "active": "true",
        "deadline": random.randint(1, 14),
    }
    gen.set_template(template)
    return gen.document()
