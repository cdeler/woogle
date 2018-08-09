from django.contrib import admin
import requests
# Register your models here.

from crawler.database_binding import init_db, reparse_by_id
from crawler.pagerank import compute_pagerank
from crawler.WikiSpider import execute_spider
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages

from wikisearch.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    change_list_template = "buttons.html"
    list_display = (
        'title',
        'url',
        'text',
        'page_rank'
    )

    actions = ['reindex','reparse']

    def reindex(self, request, queryset):
        """
        Admin action that send post request with quetyset to elasticsearch service.
        """
        result = True
        for row in queryset.values('id'):
            response = requests.post("http://0.0.0.0:9999", data = str(row['id']))
            if response.content.decode('ascii') != f'{str(row["id"])} is executed':
                result = False
        if result:
            self.message_user(request, 'Articles ware successfully indexed')

    def reparse(self, request, queryset):
        """
        Admin action that force crawler parse article of queryset in database.
        """
        for row in queryset.values('id'):
            session = init_db()
            reparse_by_id(session,row['id'])

    def get_urls(self):
        """
        Function creates urls for post requests from django admin panel.
        """
        urls = super().get_urls()
        my_urls = [
            path('parse_articles/', self.crawler_executor),
            path('put_into_elastic/', self.connector_executor),
            path('compute_pagerank/', self.cumpute_pagerank)
        ]
        return my_urls + urls

    def crawler_executor(self, request):
        """
        Custom admin action that execute crawler.
        """
        execute_spider()
        self.message_user(request, "Crawler has been successfully executed")
        return HttpResponseRedirect("../")

    def connector_executor(self, request):
        """
        Custom admin action that send request to connector which takes all data from database and send
         to elasticsearch service.
        """
        try:
            response = requests.post("http://0.0.0.0:9999", data='index')
            if response.content.decode('ascii') == 'index is executed':
                self.message_user(request, 'Connector has been successfully executed')
        except:
            self.message_user(request, 'Connector execution failed',level=messages.ERROR)

        return HttpResponseRedirect("../")

    def cumpute_pagerank(self, request):
        """
        Custom admin action that computes pagerank from articles in database.
        """
        result = compute_pagerank()
        if result:
            self.message_user(request, "Pagerank has been successfully computed")
        else:
            self.message_user(request, 'Computation failed', level=messages.ERROR)
        return HttpResponseRedirect("../")


    reindex.short_description = 'Reindex articles'
    reparse.short_description = 'Reparse articles'