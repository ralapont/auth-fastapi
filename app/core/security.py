import bcrypt

def get_password_hash(password: str) -> str:
    # 1. Convertimos el string a bytes
    password_bytes = password.encode('utf-8')
    # 2. Generamos la sal (salt)
    salt = bcrypt.gensalt(rounds=12, prefix=b"2b")
    # 3. Hasheamos directamente con la librería de C
    hashed = bcrypt.hashpw(password_bytes, salt)
    # 4. Devolvemos como string para la DB
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Comparamos bytes contra el hash guardado
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )