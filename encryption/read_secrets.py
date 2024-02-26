import os
import dotenv
from .encryptor import Encryptor


def setenv(encryptor, key, enc_val):
    """Set environment variables from key-enc pair"""
    val = encryptor.decrypt(enc_val)
    os.environ[key] = val


def load_dotenv(keyfile='key.bin', load_secrets=True):
    """Load environment variables from .env file"""
    # First load the unencrypted .env file
    dotenv.load_dotenv()

    # Then load the encrypted key-value pairs (if requested)
    if not load_secrets:
        return
    encryptor = Encryptor.load(keyfile)
    env = dotenv.dotenv_values('secrets.env')
    for key, enc_val in env.items():
        setenv(encryptor, key, enc_val)
