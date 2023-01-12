from cryptography.fernet import Fernet

from app.core.config import CRYPT_KEY

key = str.encode(CRYPT_KEY)
fernet = Fernet(key)


def get_encrypted_string(text: str):
    return fernet.encrypt(text.encode()).decode()


def get_decrypted_string(text: str):
    return fernet.decrypt(str.encode(text)).decode()
