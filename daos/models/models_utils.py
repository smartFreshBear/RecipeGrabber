from uuid import uuid4

def generate_uuid():
    return str(uuid4())

def auto_str(cls):
    def __str__(self):
        return str({column.name: getattr(self, column.name)
            for column in type(self).__table__.columns})
    
    cls.__str__ = __str__
    return cls

def validate_empty_string(key, value):
    if value.strip() == "":
        raise ValueError(f"{key} cannot be empty.")
    return value.strip()