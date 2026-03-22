class AuthInvalidCredentiasl(Exception):
    """Se lanza cuando falla por invalid credentials"""
    pass

class AuthUserLocked(Exception):
    """Se lanza cuando el user esta bloqueado"""
    pass
