class UsersMocks:
    def get_users(self):
        users = [
            {"firstName": "firstName", "lastName": "Doe"},
            {"firstName": "lastName", "lastName": "b"},
        ]

        return users
