import base64
import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass


class Encryptor:
    def __init__(self, salt, password):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000)
        self._fernet = Fernet(base64.urlsafe_b64encode(kdf.derive(password)))

    def encrypt(self, message):
        message_str = json.dumps(message)
        message_bytes = message_str.encode('utf-8')
        enc_bytes = self._fernet.encrypt(message_bytes)
        enc_b64 = base64.b64encode(enc_bytes)
        enc_str = enc_b64.decode('utf-8')
        return enc_str
    
    def decrypt(self, enc_str):
        enc_b64 = enc_str.encode('utf-8')
        enc_bytes = base64.b64decode(enc_b64)
        message_bytes = self._fernet.decrypt(enc_bytes)
        message_str = message_bytes.decode('utf-8')
        message = json.loads(message_str)
        return message
    
    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            salt = f.read(16)
        password = os.getenv('ENC_KEY_PWD')
        if password is None:
            print('No password found in environment')
            password = getpass.getpass(
                'Enter password for loaded key: ')
        password = password.encode('utf-8')
        return cls(salt, password)
    
    @classmethod
    def generate(cls, path):
        password = getpass.getpass(
            'Enter password for new key: ').encode('utf-8')
        salt = os.urandom(16)
        with open(path, 'wb') as f:
            f.write(salt)
        return cls(salt, password)

