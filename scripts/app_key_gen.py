import secrets

secret_key = secrets.token_hex(24)  # Generates 24 random bytes
print(secret_key)  # Prints the key in hexadecimal format
