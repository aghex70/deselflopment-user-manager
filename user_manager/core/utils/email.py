import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail, To

from ..settings import (
    ENVIRONMENT,
    FROM_EMAIL,
    LOCAL_URL,
    PRODUCTION_URL,
    SENDGRID_API_KEY,
)


def send_email(subject: str, body: str, destination: str) -> tuple[bool, str | None]:
    _sendgrid = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(FROM_EMAIL)
    to_email = To(destination)
    mail = Mail(from_email, to_email, subject, body)
    mail_json = mail.get()

    try:
        response = _sendgrid.client.mail.send.post(request_body=mail_json)
    except Exception as e:
        return False, str(e)

    if response.status_code != 202:
        return False, f"Error sending email: {response.status_code}"

    return True, None


def generate_welcome_email(user) -> tuple[str, str]:
    subject = "👋👋👋 Welcome to deselflopment!!! 👋👋👋"
    origin = LOCAL_URL if ENVIRONMENT == "local" else PRODUCTION_URL
    origin += "/activate/" + user.activation_code
    body = f"In order to complete your registration, please click on the following link:\n\n {origin}"
    return subject, body


def generate_password_reset_email(user) -> tuple[str, str]:
    subject = "🔑🔑🔑 Password reset request 🔑🔑🔑"
    origin = LOCAL_URL if ENVIRONMENT == "local" else PRODUCTION_URL
    origin += "/reset-password/" + user.reset_password_code
    body = f"In order to reset your password, please click on the following link:\n\n {origin}"
    return subject, body
