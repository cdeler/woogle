from django.shortcuts import render
from wikisearch.models import Article
# Create your views here.

from django.views.generic.list import  ListView


class ArticleListView(ListView):
    model = Article
    paginate_by = 3
    template_name = 'index.html'