from .shared_code import *

def tags(request):
    context = {}
    return render(request, 'viewer/tags.html', context)