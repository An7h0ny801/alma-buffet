import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from werkzeug.security import check_password_hash


_HASHER = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)
_PREFIJO_ARGON2 = "$argon2id$"


def generar_hash(password):
    return _HASHER.hash(password)


def verificar_hash(hash_guardado, password):
    hash_guardado = hash_guardado or ""
    if hash_guardado.startswith("$argon2"):
        try:
            return _HASHER.verify(hash_guardado, password)
        except (VerificationError, InvalidHashError):
            return False
    if "$" not in hash_guardado:
        return False
    try:
        return check_password_hash(hash_guardado, password)
    except (ValueError, TypeError):
        return False


def necesita_actualizarse(hash_guardado):
    if not (hash_guardado or "").startswith(_PREFIJO_ARGON2):
        return True
    try:
        return _HASHER.check_needs_rehash(hash_guardado)
    except InvalidHashError:
        return True


_HASH_FICTICIO = generar_hash(secrets.token_urlsafe(24))


def consumir_tiempo_de_verificacion(password):
    verificar_hash(_HASH_FICTICIO, password or "")
    return False
