from django.template.loader import render_to_string
from core.tasks import send_mail_task


def send_talk_invitation_mail(talk):
    subject = "Online Events | Talk Invitation"
    message = render_to_string(
        "talks/invitation_mail.html",
        {
            "speaker_username": talk.speaker.username,
            "organizer_username": talk.event.organizer.username,
            "event_title": talk.event.title,
        },
    )

    send_mail_task.delay(subject, message, [talk.speaker.email])
