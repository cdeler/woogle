from django.contrib import admin

# Register your models here.
from .models import Article


from wikisearch.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'url',
        'text',
        'page_rank'
    )
