from dataclasses import dataclass
from sqlalchemy.orm import validates

from daos.models.models_utils import auto_str, generate_uuid, validate_empty_string


def define_user(db):

    @auto_str
    @dataclass(init=True, repr=True, eq=True)
    class User(db.Model):
        __table_args__ = {"extend_existing": True}
        id: str = db.Column(db.String(36), primary_key=True, default=generate_uuid)
        firstName: str = db.Column(db.String(250), nullable=False, unique=True)
        lastName: str = db.Column(db.String(250), nullable=False)

        @validates("firstName")
        def validate_firstName(self, key, value):
            return validate_empty_string(key, value)

    return User
