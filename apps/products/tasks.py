from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model


LOW_STOCK_THRESHOLD = 5


@shared_task
def check_low_stock_task():
    from products.models import Product

    low_stock_products = list(
        Product.objects.filter(stock__lte=LOW_STOCK_THRESHOLD, stock__gte=0)
        .order_by("stock")
        .only("id", "name", "stock")
    )

    if not low_stock_products:
        return "No low stock products found"

    admin_users = get_user_model().objects.filter(is_staff=True, is_active=True)
    admin_emails = [admin.email for admin in admin_users if admin.email]

    if not admin_emails:
        return "No admin users with email found"

    context = {
        "low_stock_products": low_stock_products,
        "threshold": LOW_STOCK_THRESHOLD,
        "site_url": settings.ALLOWED_HOSTS[0]
        if settings.ALLOWED_HOSTS
        else "http://127.0.0.1:8000",
    }

    html_message = render_to_string("emails/low_stock.html", context)
    plain_message = f"""
Low Stock Alert ⚠️

The following products have low stock levels:

{chr(10).join([f"- {p.name}: Only {p.stock} left" for p in low_stock_products])}

Please review these items and update stock levels.

Admin Panel: {context["site_url"]}/admin/products/product/

Best regards,
Smart S3r System
    """

    send_mail(
        subject=f"⚠️ Low Stock Alert - {len(low_stock_products)} products need attention",
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=admin_emails,
        html_message=html_message,
        fail_silently=False,
    )

    return f"Low stock alert sent to {len(admin_emails)} admin(s) for {len(low_stock_products)} products"


@shared_task
def check_and_notify_low_stock_task():
    from products.models import Product
    from django.db.models import F

    newly_low = Product.objects.filter(
        stock__lte=LOW_STOCK_THRESHOLD, stock__gt=0
    ).only("id", "name", "stock")

    if not newly_low.exists():
        return "No products with low stock"

    newly_low_list = list(newly_low)

    admin_users = get_user_model().objects.filter(is_staff=True, is_active=True)
    admin_emails = [admin.email for admin in admin_users if admin.email]

    if not admin_emails:
        return "No admin users with email found"

    context = {
        "low_stock_products": newly_low_list,
        "threshold": LOW_STOCK_THRESHOLD,
        "site_url": settings.ALLOWED_HOSTS[0]
        if settings.ALLOWED_HOSTS
        else "http://127.0.0.1:8000",
    }

    html_message = render_to_string("emails/low_stock.html", context)

    send_mail(
        subject=f"⚠️ Low Stock Alert - {len(newly_low_list)} products",
        message=f"Low stock alert for {len(newly_low_list)} products",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=admin_emails,
        html_message=html_message,
        fail_silently=False,
    )

    return f"Low stock notification sent for {len(newly_low_list)} products"
