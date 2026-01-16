from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Post."""

    list_display = ('title', 'author', 'pub_date', 'category', 'is_published')
    list_display_links = ('title',)
    list_filter = ('category', 'is_published', 'pub_date')
    search_fields = ('title', 'text')
    list_per_page = 20


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Category."""

    list_display = ('title', 'slug', 'is_published')
    list_display_links = ('title',)
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}  # Автозаполнение slug


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Location."""

    list_display = ('name', 'is_published')
    list_display_links = ('name',)
    list_filter = ('is_published',)
    search_fields = ('name',)
