from django.conf import settings
from django.http import HttpResponseForbidden


class Whitelist(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')  # Get client IP
        if ip[:7] != "147.251" and not settings.DEBUG:
            return HttpResponseForbidden()
        return self.get_response(request)
