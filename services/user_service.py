from daos.models.users.user_model import define_user


class UserService:
    def __init__(self, crud):
        self.crud = crud
        self.User = define_user(crud.db)
