class User:
    # CONSTACTOR
    def __init__(self, name, password, user_id=None, numPlay=0, win=0):
        self.name = name
        self.user_id  = user_id
        self.password = password
        self.numPlay = numPlay
        self.win = win
        self.words = ()
    # JSON
    def to_dict(self):
        return {
            'name': self.name,
            'id': self.user_id,
            'password': self.password,
            'numPlay': self.numPlay,
            'words': self.words,
            'win': self.win,
        }
    # TO STRING
    def __str__(self):
        return (f"Player: {self.name}\n"
                f"ID: {self.id}\n"
                f"Victories: {self.win}\n"
                f"Words: {', '.join(self.words)}\n")
