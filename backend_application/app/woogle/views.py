from django.http import HttpResponse
from django.shortcuts import render_to_response


def main(request):
    return HttpResponse("index.html")
