def to_lower_case(data: str):
    return data.lower()


regex = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*+=]).{8,}$"
