from dataclasses import dataclass
from datetime import datetime


def define_broken_link(db):
    @dataclass
    class BrokenLink(db.Model):
        __table_args__ = {'extend_existing': True}
        id: int = db.Column(db.Integer, primary_key=True)
        url: str = db.Column(db.String(200), unique=True, nullable=False)
        taken_care_of: bool = db.Column(db.Boolean, unique=False, nullable=False)
        date: datetime = db.Column(db.DateTime, unique=False, nullable=True)

    return BrokenLink
