import re

regex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*+=]).{8,}$"


def validate_stack_and_track(values):
    backend_tracks = ["nodejs", "python", "php", "golang"]
    frontend_tracks = ["vuejs", "reactjs", "vanillajs"]
    design_tracks = ["product design", "graphic design"]
    stack = values.get("stack")
    track = values.get("track")

    if stack and not track or track and not stack:
        stack_with_tracks = ["backend", "frontend", "design"]
        if stack and stack in stack_with_tracks:
            msg = "Track field is required"
        elif stack:
            return values
        else:
            msg = "Stack field is required"
        raise ValueError(msg)
    if stack == "backend" and track not in backend_tracks:
        raise ValueError("Track selected not a backend track")
    if stack == "frontend" and track not in frontend_tracks:
        raise ValueError("Track selected not a frontend track")
    if stack == "design" and track not in design_tracks:
        raise ValueError("Track selected not a design track")
    return values


def validate_password(values):
    password = values.get("password")
    if not re.match(regex, password):
        raise ValueError(
            "Password must contain Min. 8 characters, 1 Uppercase,\
            1 lowercase, 1 number, and 1 special character"
        )
    return values


def to_lower_case(data: str):
    return data.lower()


def get_queryset(user):
    return {
        "stage": user.stage,
        "stack": user.stack,
        "track": user.track,
        "proficiency": user.proficiency,
    }
