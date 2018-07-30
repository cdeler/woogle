from django.contrib import admin
import requests
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

    actions = ['reindex','reparse']

    def reindex(self, request, queryset):
        result = True
        for row in queryset.values('id'):
            response = requests.post("http://0.0.0.0:9999", data = str(row['id']))
            if response.content.decode('ascii') != f'{str(row["id"])} is executed':
                result = False
        if result:
            self.message_user(request, 'Articles ware successfully indexed')

    def reparse(self, request, queryset):
        pass

    reindex.short_description = 'Put article in elastic again'
    reparse.short_description = 'Parse article again in database'

