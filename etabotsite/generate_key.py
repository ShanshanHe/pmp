"""Generates a key that can be used in django_keys_prod.json."""

from cryptography.fernet import Fernet

s = Fernet.generate_key()
print(s.decode('utf-8'))
