from django.core.cache import cache
from django.shortcuts import render
from django.db.models import Count
from django.views.decorators.http import require_POST
from products.models import Category, Product
from .models import Banner
from django.urls import translate_url
from django.http import HttpResponseRedirect
from django.conf import settings


@require_POST
def set_language_custom(request):
    next_url = request.POST.get("next", "/")
    lang_code = request.POST.get("language")
    # Translate the URL to the new language (adds/removes prefix)
    translated_url = translate_url(next_url, lang_code)
    response = HttpResponseRedirect(translated_url)
    # Optional: set the language cookie for consistency
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


def home(request):
    categories = cache.get("home_categories")
    if categories is None:
        categories = list(Category.objects.all()[:4])
        cache.set("home_categories", categories, 3600)

    # Featured Products (newest)
    featured_products = cache.get("featured_products")
    if featured_products is None:
        featured_products = list(
            Product.objects.select_related("brand")
            .only(
                "id",
                "name",
                "slug",
                "img",
                "img_link",
                "price",
                "brand__id",
                "brand__name",
            )
            .all()[:8]
        )
        cache.set("featured_products", featured_products, 3600)

    most_liked = cache.get("most_liked_products")
    if most_liked is None:
        most_liked = list(
            Product.objects.select_related("brand")
            .annotate(wishlist_count=Count("wishlist"))
            .filter(wishlist_count__gt=0)
            .order_by("-wishlist_count")
            .only(
                "id",
                "name",
                "slug",
                "img",
                "img_link",
                "price",
                "brand__id",
                "brand__name",
            )[:8]
        )
        cache.set("most_liked_products", most_liked, 1800)

    # Banners
    banners = cache.get("home_banners")
    # If here is no Caching make caching
    if banners is None:
        banners = list(Banner.objects.filter(is_active=True))
        cache.set("home_banners", banners, 3600)

    context = {
        "categories": categories,
        "featured_products": featured_products,
        "most_liked_products": most_liked,
        "banners": banners,
    }
    return render(request, "pages/home.html", context)
