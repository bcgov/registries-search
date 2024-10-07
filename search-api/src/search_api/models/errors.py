class DbRowNotFound(Exception):
    """Row not found in database"""
    def __init__(self):
        self.message = "not.found.in.db"
        super().__init__(self.message)
