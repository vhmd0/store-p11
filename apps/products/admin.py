from django.contrib import admin
from .models import Category, Brand, Tag, Product, Review, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count")
    list_editable = ("slug",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    actions = ["delete_selected"]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            actions["delete_selected"] = (
                actions["delete_selected"][0],
                "delete_selected",
                "Delete selected categories",
            )
        return actions

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Products"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count")
    list_editable = ("slug",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    actions = ["delete_selected"]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            actions["delete_selected"] = (
                actions["delete_selected"][0],
                "delete_selected",
                "Delete selected brands",
            )
        return actions

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Products"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count")
    list_editable = ("slug",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    actions = ["delete_selected"]

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "stock", "category", "brand", "created_at")
    list_editable = ("price", "stock", "sku")
    list_filter = ("category", "brand", "tags", "created_at")
    search_fields = ("name", "description", "sku")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("tags",)
    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "sku", "description")}),
        ("Pricing & Inventory", {"fields": ("price", "stock", "type")}),
        ("Organization", {"fields": ("category", "brand", "tags")}),
        ("Links & Media", {"fields": ("external_link", "img", "img_link")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
    actions = ["delete_selected", "update_stock"]
    list_per_page = 25

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            actions["delete_selected"] = (
                actions["delete_selected"][0],
                "delete_selected",
                "Delete selected products",
            )
        return actions

    @admin.action(description="Update stock to specified value")
    def update_stock(self, request, queryset):
        # This would need custom form for input
        pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at", "comment_preview")
    list_filter = ("rating", "created_at", "product__category")
    search_fields = ("product__name", "user__user__username", "comment")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 20
    actions = ["approve_reviews", "delete_reviews"]

    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment

    comment_preview.short_description = "Comment"

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        # For now just count them
        queryset.count()

    @admin.action(description="Delete selected reviews")
    def delete_reviews(self, request, queryset):
        queryset.delete()


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("created_at", "product__category")
    search_fields = ("user__user__username", "product__name")
