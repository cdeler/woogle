from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from wikisearch.models import Article
from django.template import Context, loader
import json
# Create your views here.
import requests
from functools import reduce


from django.views.generic.list import ListView
from .forms import SearchRequest

class ArticleListView(ListView):
    form_class = SearchRequest
    model = Article
    paginate_by = 10
    template_name = 'search_page.html'
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




# AUTOCOMPLETE SUGGESTION (need to set connection between rest api and django)
def search_page(request):
    """

    :param request:
    :return:
    """
    template = loader.get_template("search_page.html")
    html = template.render()
    return HttpResponse(html)


def get_user_query(request):
    """

    :param request:
    :return:
    """
    if request.method == "GET":
        user_query = request.GET.get("user_query")
        find__title_pages = load_pages(user_query)
        return HttpResponse(find__title_pages)


def load_pages(user_query):
    """

    :param user_query:
    :return:
    """
    # setting host/port with config.ini
    host = "rest_api"
    port = 5000

    url = "http://{host}:{port}/?index=wiki&doc_type=page&search=%22{q}%22".format(q=user_query,host=host, port=port)
    try:
        response = requests.get(url, timeout=(40, 40)).json()
    except requests.exceptions.ReadTimeout:
        print('Oops. Read timeout occured')
    except requests.exceptions.ConnectTimeout:
        print('Oops. Connection timeout occured!')
    else:
        return change_response_json(response)


def change_response_json(obj_json):
    """

    :param obj_json:
    :return:
    """
    array_dicts = obj_json["suggest"]["title_suggestion"][0]["options"]
    pages = []
    for i, key in enumerate(array_dicts):
        pages.append(array_dicts[i]["_source"])
        pages[i]["content"] = pages[i]["content"][:100]
    rt = json.dumps(pages)
    return rt
