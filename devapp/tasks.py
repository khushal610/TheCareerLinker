# celery tasks
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_online_session_email(student_email, topic_name, student_name, start_time, end_time, dev_name, company_name):
    subject = f"Reminder - {topic_name}"
    message = f"""
    <p>Dear {student_name},</p>

    <p>I hope this message finds you well.</p>

    <p>I am writing to remind you about the upcoming session scheduled to start within the next 5 minutes or soon. Please find the session details below:</p>

    <h4>{topic_name} Session starts at {start_time} and will end at {end_time}. This session is scheduled by {dev_name} from {company_name}.</h4>

    <p>Instructions for the Student: Please stay active and check for notifications to find and join suitable online sessions according to your needs. It is essential to ensure that you are prepared and ready to join the session promptly.</p>

    <p>Thank you for your attention to this matter. Should you have any questions or require further assistance, please do not hesitate to reach out.</p>
    <br>
    Best regards,<br>
    The Career Linker Team
    </p>
    """
    from_email = settings.EMAIL_HOST_USER
    to_email = student_email
    send_mail(subject, '', from_email, [to_email], html_message=message)