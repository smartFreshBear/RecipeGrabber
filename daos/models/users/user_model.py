from dataclasses import dataclass
from uuid import uuid4


def define_user(db):
    @dataclass
    class User(db.Model):
        __table_args__ = {'extend_existing': True}
        id: str = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
        firstName: str = db.Column(db.String(250), nullable=False)
        lastName: str = db.Column(db.String(250), nullable=False)

    return User