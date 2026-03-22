from django.core.cache import cache
from .models import Category, Wishlist


def menu_categories(request):
    categories = cache.get("menu_categories")
    if categories is None:
        categories = list(Category.objects.all()[:10])
        cache.set("menu_categories", categories, 3600)

    count = cache.get("category_count")
    if count is None:
        count = Category.objects.count()
        cache.set("category_count", count, 3600)

    return {"menu_categories": categories, "has_more_categories": count > 10}


def wishlist(request):
    count = 0
    if request.user.is_authenticated:
        try:
            count = Wishlist.objects.filter(user=request.user.profile).count()
        except Exception:
            pass
    return {"wishlist_count": count}
