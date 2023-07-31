from daos.models.users.user_model import define_user
class UserService:
    def __init__(self, db):
        self.db = db
        self.StoredRecipe = define_user(self.db)
