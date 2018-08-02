from django.shortcuts import render
from django.http import HttpResponseRedirect
from wikisearch.models import Article
# Create your views here.
import requests
from functools import reduce


from django.views.generic.list import ListView
from .forms import SearchRequest

class ArticleListView(ListView):
    form_class = SearchRequest
    model = Article
    paginate_by = 10
    template_name = 'index.html'
    queryset = []


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context

    def get_queryset(self):
        form = SearchRequest(self.request.GET)
        if form.is_valid():
            # url = "http://127.0.0.1:5000"
            # querystring = {
            #     "index": 'wiki',
            #     "doc_type": 'page',
            #     "search":form.cleaned_data['search_req']}
            # response = requests.request("GET", url, params=querystring).json()
            # match = [i['_id'] for i in response['hits']['hits']]

            match = [10, 11] #Delete this and uncomments above when everithing is ready
            articles = [Article.objects.filter(id=article_id) for article_id in match]
            articles = reduce(Article.objects.union, articles, Article.objects.none())
            return articles
        return Article.objects.all()

