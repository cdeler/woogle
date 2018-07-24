from django.contrib import admin

# Register your models here.

from wikisearch.models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass