class User:

    def __init__(self):
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.id = ":)"

    def get_id(self):
        return self.id
