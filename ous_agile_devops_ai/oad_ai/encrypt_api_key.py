#encrypt_api_key
from cryptography.fernet import Fernet

# Generate an encryption key
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

# Your API key
api_key = b'B1xJInq9KnjrEurPCS3N1K9I1KNyyvIh'

# Encrypt the API key
encrypted_api_key = cipher_suite.encrypt(api_key)

# Save the encryption key and the encrypted API key to files
with open('encryption_key.txt', 'wb') as key_file:
    key_file.write(encryption_key)

with open('encrypted_api_key.txt', 'wb') as encrypted_key_file:
    encrypted_key_file.write(encrypted_api_key)

print("Encryption key and encrypted API key have been saved to files.")
