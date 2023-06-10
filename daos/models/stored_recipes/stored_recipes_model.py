from dataclasses import dataclass


def define_stored_recipe(db):
    @dataclass
    class StoredRecipe(db.Model):
        __table_args__ = {'extend_existing': True}
        id: int = db.Column(db.Integer, primary_key=True)
        url: str = db.Column(db.String(250), unique=True, nullable=False)
        title: str = db.Column(db.String(250), nullable=False)
        ingredients: list = db.Column(
                db.PickleType(), nullable=False, default=[]
                )
        instructions: list = db.Column(
                db.PickleType(), nullable=False, default=[]
                )

    return StoredRecipe
