from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from products.models import Product
from orders.models import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus


def get_cart(request):
    """Get cart from session."""
    return request.session.get("cart", {})


def save_cart(request, cart):
    """Save cart to session."""
    request.session["cart"] = cart
    request.session.modified = True


def get_cart_products(request):
    """
    Get cart products with quantities and totals.
    Single IN-query with select_related — no N+1.
    """
    cart = get_cart(request)
    if not cart:
        return [], 0

    product_ids = [int(pid) for pid in cart]
    product_dict = {
        p.id: p
        for p in Product.objects.filter(id__in=product_ids)
        .select_related("brand")
        .only(
            "id", "name", "slug", "img", "img_link", "price", "brand__id", "brand__name"
        )
    }

    items = []
    total = 0
    for pid_str, quantity in cart.items():
        product = product_dict.get(int(pid_str))
        if product and quantity > 0:
            subtotal = product.price * quantity
            total += subtotal
            items.append(
                {"product": product, "quantity": quantity, "subtotal": subtotal}
            )

    return items, total


@login_required
def checkout(request):
    """Checkout page — display cart items and shipping form."""
    products, total = get_cart_products(request)

    if not products:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:detail")

    from users.models import Address

    addresses = Address.objects.filter(user=request.user).order_by(
        "-is_default", "-created_at"
    )
    default_address = addresses.filter(is_default=True).first()

    default_phone = default_address.phone if default_address else ""
    default_shipping = ""
    if default_address:
        default_shipping = (
            f"{default_address.address}, {default_address.area}, {default_address.city}"
            if default_address.area
            else f"{default_address.address}, {default_address.city}"
        )

    return render(
        request,
        "orders/checkout.html",
        {
            "products": products,
            "total": total,
            "default_phone": default_phone,
            "default_address": default_shipping,
            "addresses": addresses,
        },
    )


from django.db import transaction

@login_required
def create_order(request):
    """Create order from cart with stock validation and reduction."""
    if request.method != "POST":
        return redirect("orders:checkout")

    products, total = get_cart_products(request)

    if not products:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:detail")

    shipping_address = request.POST.get("shipping_address", "").strip()
    phone = request.POST.get("phone", "").strip()
    notes = request.POST.get("notes", "").strip()

    if not shipping_address or not phone:
        messages.error(request, "Please provide shipping address and phone number.")
        return redirect("orders:checkout")

    try:
        with transaction.atomic():
            # Validate and reduce stock for each product
            for item in products:
                product = item["product"]
                requested_qty = item["quantity"]
                
                # Refetch product within transaction to lock the row
                p = Product.objects.select_for_update().get(id=product.id)
                
                if p.stock < requested_qty:
                    messages.error(request, f"Sorry, {p.name} is out of stock or does not have enough quantity (Available: {p.stock}).")
                    return redirect("orders:checkout")
                
                # Reduce stock
                p.stock -= requested_qty
                p.save(update_fields=["stock"])

            # Create the order
            order = Order.objects.create(
                user=request.user,
                status=OrderStatus.PENDING,
                payment_method=PaymentMethod.CASH_ON_DELIVERY,
                payment_status=PaymentStatus.PENDING,
                total_amount=total,
                shipping_address=shipping_address,
                phone=phone,
                notes=notes if notes else None,
            )

            # Bulk-create order items
            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        product=item["product"],
                        quantity=item["quantity"],
                        price=item["product"].price,
                    )
                    for item in products
                ]
            )

            # Clear the cart
            save_cart(request, {})
            
            messages.success(request, "Your order has been placed successfully!")
            return redirect("orders:confirmation", order_id=order.id)
            
    except Exception as e:
        # If anything fails (like a database error), the transaction rolls back
        messages.error(request, f"An error occurred while processing your order: {str(e)}")
        return redirect("orders:checkout")


@login_required
def order_confirmation(request, order_id):
    """Order confirmation page."""
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product__brand"),
        id=order_id,
        user=request.user,
    )
    return render(
        request,
        "orders/order_confirmation.html",
        {
            "order": order,
            "items": order.items.all(),  # uses the already-prefetched cache
        },
    )


@login_required
def order_list(request):
    """User's order history."""
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__product")
        .only("id", "status", "total_amount", "created_at", "payment_status")
    )
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    """Order detail page — prefetch items + product in one query."""
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product__brand"),
        id=order_id,
        user=request.user,
    )
    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
            "items": order.items.all(),  # uses the already-prefetched cache
        },
    )


@login_required
@transaction.atomic
def cancel_order(request, order_id):
    """Cancel order and restore product stock."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in [OrderStatus.CANCELLED, OrderStatus.DELIVERED, OrderStatus.SHIPPED]:
        messages.error(request, f"Order cannot be cancelled in its current status: {order.get_status_display()}.")
        return redirect("orders:order_detail", order_id=order.id)

    # Restore stock for each item
    for item in order.items.select_related("product"):
        product = item.product
        product.stock += item.quantity
        product.save(update_fields=["stock"])

    order.status = OrderStatus.CANCELLED
    order.save(update_fields=["status"])

    messages.success(request, f"Order #{order.id} has been cancelled and stock restored.")
    return redirect("orders:order_detail", order_id=order.id)
