import bcrypt


def hash_secret(secret: str) -> str:
    encoded = secret.encode("utf-8")
    if len(encoded) > 72:
        raise ValueError("O segredo não pode exceder 72 bytes para bcrypt")
    return bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_secret(secret: str, secret_hash: str) -> bool:
    try:
        return bcrypt.checkpw(secret.encode("utf-8"), secret_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
