from django.core.cache import cache
from .models import Category, Wishlist


def menu_categories(request):
    categories = cache.get("menu_categories")
    has_more = cache.get("has_more_categories")

    if categories is None:
        # Fetch all categories in one query, derive count from Python — no second COUNT(*)
        all_cats = list(Category.objects.only("id", "name", "name_ar", "slug").all())
        has_more = len(all_cats) > 10
        categories = all_cats[:10]
        cache.set("menu_categories", categories, 3600)
        cache.set("has_more_categories", has_more, 3600)

    return {"menu_categories": categories, "has_more_categories": has_more}


def wishlist(request):
    count = 0
    if request.user.is_authenticated:
        try:
            cache_key = f"wishlist_count_{request.user.id}"
            count = cache.get(cache_key)
            if count is None:
                count = Wishlist.objects.filter(user=request.user.profile).count()
                cache.set(cache_key, count, 300)  # 5 min cache
        except Exception:
            pass
    return {"wishlist_count": count}
