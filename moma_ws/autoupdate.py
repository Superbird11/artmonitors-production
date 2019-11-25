"""
A script that uses the local keys and codes to authenticate a request to localhost
to upload the most recently-uploaded collection. Can only be successfully run
locally.

This file is intended to be run automatically by a cron job (or some other task
scheduler) on the server.

Python packages that must be installed globally for this to work:
- requests
- pycrypto

Crontab line:
0 17 * * 1 cd /.../moma_ws && /usr/local/bin/python3.7 autoupdate.py

"""
import base64
import requests
import json
import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def decrypt_message(encoded_encrypted_msg, private_key):
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    decryptor = PKCS1_OAEP.new(private_key)
    decoded_decrypted_msg = decryptor.decrypt(decoded_encrypted_msg)
    return decoded_decrypted_msg


def encrypt_message(a_message, public_key):
    encryptor = PKCS1_OAEP.new(public_key)
    encrypted_msg = encryptor.encrypt(a_message)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)  # base64 encoded strings are database friendly
    return encoded_encrypted_msg


if __name__ == "__main__":
    print("Starting auto-upload trigger")
    # retrieve and encode key
    with open('artmonitors/keys/upload_preload_random_key', 'rb') as random_key_file:
        random_string = random_key_file.read()
    with open('artmonitors/keys/upload_preload_rsa_key.pub', 'rb') as rsa_key_file:
        public_key = RSA.importKey(rsa_key_file.read())
    key = encrypt_message(random_string, public_key)

    # set data
    data = {"key": key.decode("utf-8")}

    # prepare request
    url = sys.argv[1] if len(sys.argv) >= 2 else "https://artmonitors.com/upload_preloaded"
    with open('artmonitors/keys/upload_preload_permissions', 'r') as auth_file:
        auth_components = auth_file.read().split('\n')
        auth = (auth_components[0], auth_components[1])

    # send request
    print("Sending request to url %s" % url)
    headers = {
        'content-type': 'application/json'
    }
    response = requests.post(url=url, data=json.dumps(data), headers=headers, auth=auth)

    # that's all
    print(f"Auto-upload trigger attempt completed. Response data:\n{response.content}")
    print(str(response.content.decode('utf-8')))
