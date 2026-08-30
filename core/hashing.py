import hashlib
import bcrypt

class SecurityHasher:
    @staticmethod
    def hash_md5(password: str) -> str:
        return hashlib.md5(password.encode('utf-8')).hexdigest()

    @staticmethod
    def hash_sha256(password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def hash_bcrypt(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_bcrypt(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))