from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


@shared_task
def send_welcome_email_task(user_id):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)

        context = {
            "user": user,
            "site_url": settings.ALLOWED_HOSTS[0]
            if settings.ALLOWED_HOSTS
            else "http://127.0.0.1:8000",
        }

        html_message = render_to_string("emails/welcome.html", context)
        plain_message = f"""
Hello {user.get_full_name() or user.username}!

Welcome to Smart S3r! Thank you for joining us.

Your account has been created successfully.

Start shopping at: {context["site_url"]}

Best regards,
Smart S3r Team
        """

        send_mail(
            subject="Welcome to Smart S3r! 🎉",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Welcome email sent to {user.email}"
    except User.DoesNotExist:
        return f"User with id {user_id} not found"
