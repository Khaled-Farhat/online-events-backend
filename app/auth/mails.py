from django.conf import settings
from django.template.loader import render_to_string
from core.tasks import send_mail_task


def send_verification_email(username, user_email, verification_key):
    subject = "Online Events | Verify Your Account"
    message = render_to_string(
        "auth/verification_link_mail.html",
        {
            "username": username,
            "verification_link": f"{settings.FRONTEND_VERIFY_EMAIL_URL}"
            f"?verification_key={verification_key}",
        },
    )

    send_mail_task.delay(subject, message, [user_email])
