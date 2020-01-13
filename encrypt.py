from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import hashes
import json
import base64

def generatePrivateKey(keySize=4096):
    key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
    return key

def PublicKeyToPEM(key):
    public = key.public_key()
    pem = public.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.PKCS1)
    return pem.decode()

def PrivateKeyToPEM(key):
    pem = key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())
    return pem.decode()

def decryptData(b64, key):
    decoded = base64.b64decode(b64)
    key = load_pem_private_key(key.encode(), password=None, backend=default_backend())
    return json.loads(key.decrypt(decoded, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(), label=None)).decode())