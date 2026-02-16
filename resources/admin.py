from django.contrib import admin
from .models import Category, Comment, Resource, ResourceLike


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "category", "is_available", "created_at"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["resource", "author", "created_at"]


@admin.register(ResourceLike)
class ResourceLikeAdmin(admin.ModelAdmin):
    list_display = ["resource", "user", "created_at"]
