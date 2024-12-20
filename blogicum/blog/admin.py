from django.contrib import admin


from .models import Category, Post, Location


# Register your models here.

@admin.register(Post)
@admin.register(Location)
@admin.register(Category)
class BlogAdmin(admin.ModelAdmin):
    list_display = (
        'post__title',
        'post__text',
        'post__author',
        'post__pub_date',
        'post__is_published',
        'location__name',
        'category__title',
        'category__description',
        'category__slug',
    )
    list_editable = (
        'is_published',
    )
