import binascii
import os
import time
import uuid

import jwt
import sendgrid
from Crypto.Cipher import AES
from sendgrid.helpers.mail import Content, Email, Mail, To

CIPHER_KEY = os.environ["CIPHER_KEY"]
CIPHER_IV = os.environ["CIPHER_IV"]
JWT_SIGNING_KEY = os.environ["JWT_SIGNING_KEY"]
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
FROM_EMAIL = os.environ["FROM_EMAIL"]

ENVIRONMENT = os.environ["ENVIRONMENT"]
PRODUCTION_URL = os.environ["PRODUCTION_URL"]
LOCAL_URL = os.environ["LOCAL_URL"]


def encrypt_password(password):
    key_string = CIPHER_KEY
    # Ensure key_string has an even number of characters
    key_string = key_string.zfill(len(key_string) + len(key_string) % 2)
    key = binascii.unhexlify(key_string)

    # Create a new AES cipher block with the IV
    iv_string = CIPHER_IV
    # Ensure iv_string has an even number of characters
    iv_string = iv_string.zfill(len(iv_string) + len(iv_string) % 2)
    iv = binascii.unhexlify(iv_string)
    block = AES.new(key, AES.MODE_CBC, iv)

    # Convert the password to a byte string and pad it so that its length is
    # a multiple of the block size
    input_bytes = password.encode("utf-8")
    padding = AES.block_size - len(input_bytes) % AES.block_size
    input_bytes += bytes([padding] * padding)

    # Encrypt the input using the CBC cipher mode
    encrypted_bytes = block.encrypt(input_bytes)

    # Convert the encrypted input to a hexadecimal string
    encrypted_hex = binascii.hexlify(encrypted_bytes).decode("utf-8")

    return encrypted_hex


def decrypt_password(ciphered_password):
    # Convert the ciphertext from a hexadecimal string to a bytes object
    encrypted = binascii.unhexlify(ciphered_password)

    key_string = CIPHER_KEY
    # Ensure key_string has an even number of characters
    key_string = key_string.zfill(len(key_string) + len(key_string) % 2)
    key = binascii.unhexlify(key_string)

    iv_string = CIPHER_IV
    # Ensure iv_string has an even number of characters
    iv_string = iv_string.zfill(len(iv_string) + len(iv_string) % 2)
    iv = binascii.unhexlify(iv_string)

    # Create a new AES cipher block with the IV
    block = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the ciphertext using the CBC cipher mode
    decrypted = block.decrypt(encrypted)

    # Remove the padding from the decrypted password
    padding = decrypted[-1]
    decrypted = decrypted[:-padding]

    # Return the decrypted password as a string
    return decrypted.decode("utf-8")


def generate_jwt_token(db_user):
    # Define your custom claims
    claims = {
        "user_id": db_user.id,
        "admin": db_user.admin,
        "sub": db_user.email,
        "exp": int(time.time())
        + 96 * 60 * 60,  # Set the expiration time to 96 hours from now
    }

    # Define your signing key
    my_signing_key = "your_hmac_secret_key"  # Replace with your actual HMAC secret key

    # Generate a JWT token with the custom claims and signing key
    token = jwt.encode(claims, my_signing_key, algorithm="HS256")
    return token


def retrieve_jwt_claims(db_user):
    # Parse the token with the secret key
    try:
        # Decode the token and verify its signature using the provided secret key and algorithm
        token = jwt.decode(
            db_user.access_token, "your_hmac_secret_key", algorithms=["HS256"]
        )
        # Extract the 'user_id' claim from the decoded token
        user_id = token["user_id"]
        return user_id, None
    except jwt.ExpiredSignatureError:
        # Handle expired token error
        return None, "Expired token"
    except jwt.InvalidTokenError:
        # Handle invalid token error
        return None, "Invalid token"


def send_email(subject: str, body: str, destination: str) -> tuple[bool, str | None]:
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(FROM_EMAIL)
    to_email = To(destination)  # Change to your recipient
    mail = Mail(from_email, to_email, subject, body)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    try:
        response = sg.client.mail.send.post(request_body=mail_json)
    except Exception as e:
        return False, e

    if response.status_code != 202:
        return False, f"Error sending email: {response.status_code}"

    return True, None


def generate_uuid():
    return str(uuid.uuid4())


def generate_welcome_email(user):
    subject = "👋👋👋 Welcome to deselflopment!!! 👋👋👋"
    origin = LOCAL_URL if ENVIRONMENT == "local" else PRODUCTION_URL
    origin += "/users/activate/" + user.activation_code
    body = f"In order to complete your registration, please click on the following link:\n\n {origin}"
    return subject, body


def generate_password_reset_email(user):
    subject = "🔑🔑🔑 Password reset request 🔑🔑🔑"
    origin = LOCAL_URL if ENVIRONMENT == "local" else PRODUCTION_URL
    origin += "/users/reset-password/" + user.reset_password_code
    body = f"In order to reset your password, please click on the following link:\n\n {origin}"
    return subject, body
