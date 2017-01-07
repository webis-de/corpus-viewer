from django.http import JsonResponse
from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'viewer/index.html', context)

def tags(request):
    context = {}
    return render(request, 'viewer/index.html', context)
