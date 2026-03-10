class UserAlreadyExistsError(Exception):
    """Se lanza cuando username o email ya están registrados."""
    pass

class UserNotFoundError(Exception):
    """Se lanza cuando un usuario no existe en la base de datos."""
    pass
