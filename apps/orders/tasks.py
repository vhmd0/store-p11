from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


@shared_task
def send_order_confirmation_task(order_id):
    from orders.models import Order, OrderItem

    try:
        order = (
            Order.objects.select_related("user")
            .prefetch_related("items__product")
            .get(id=order_id)
        )

        context = {
            "order": order,
            "order_items": order.items.all(),
            "site_url": settings.ALLOWED_HOSTS[0]
            if settings.ALLOWED_HOSTS
            else "http://127.0.0.1:8000",
        }

        html_message = render_to_string("emails/order_confirmation.html", context)
        plain_message = f"""
Order Confirmation - #{order.id}

Thank you for your order!

Order Number: #{order.id}
Status: {order.get_status_display()}
Total: {order.total_amount} EGP
Shipping Address: {order.shipping_address}
Phone: {order.phone}

We'll send you another email when your order ships.

Best regards,
Smart S3r Team
        """

        send_mail(
            subject=f"Order Confirmed! - #{order.id}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Order confirmation email sent for order #{order_id}"
    except Order.DoesNotExist:
        return f"Order #{order_id} not found"


@shared_task
def send_order_status_update_task(order_id, old_status, new_status):
    from orders.models import Order

    STATUS_MESSAGES = {
        "PENDING": "Your order is being reviewed and will be processed shortly.",
        "CONFIRMED": "Your order has been confirmed and is being prepared.",
        "PROCESSING": "Your order is being processed and packed.",
        "SHIPPED": "Your order has been shipped! You should receive it soon.",
        "DELIVERED": "Your order has been delivered. Enjoy your purchase!",
        "CANCELLED": "Your order has been cancelled.",
        "REFUNDED": "Your refund has been processed.",
    }

    try:
        order = Order.objects.select_related("user").get(id=order_id)

        context = {
            "order": order,
            "status_message": STATUS_MESSAGES.get(
                new_status, "Your order status has been updated."
            ),
            "site_url": settings.ALLOWED_HOSTS[0]
            if settings.ALLOWED_HOSTS
            else "http://127.0.0.1:8000",
        }

        html_message = render_to_string("emails/order_status.html", context)
        plain_message = f"""
Order Status Update - #{order.id}

Your order status has been updated from {old_status} to {new_status}.

{context["status_message"]}

Order Total: {order.total_amount} EGP

Best regards,
Smart S3r Team
        """

        send_mail(
            subject=f"Order Status Update - #{order.id} ({new_status})",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Status update email sent for order #{order_id}"
    except Order.DoesNotExist:
        return f"Order #{order_id} not found"


@shared_task
def send_order_cancelled_task(order_id):
    from orders.models import Order

    try:
        order = Order.objects.select_related("user").get(id=order_id)

        context = {
            "order": order,
            "cancelled_at": order.updated_at,
            "refund_message": "If you paid online, your refund will be processed within 5-7 business days.",
            "site_url": settings.ALLOWED_HOSTS[0]
            if settings.ALLOWED_HOSTS
            else "http://127.0.0.1:8000",
        }

        html_message = render_to_string("emails/order_cancelled.html", context)
        plain_message = f"""
Order Cancelled - #{order.id}

Your order #{order.id} has been cancelled.

Order Total: {order.total_amount} EGP

If you paid online, your refund will be processed within 5-7 business days.

We hope to see you again soon!

Best regards,
Smart S3r Team
        """

        send_mail(
            subject=f"Order Cancelled - #{order.id}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Cancellation email sent for order #{order_id}"
    except Order.DoesNotExist:
        return f"Order #{order_id} not found"
