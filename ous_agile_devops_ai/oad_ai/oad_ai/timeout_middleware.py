import concurrent.futures
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse
from django.conf import settings

class TimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, 'REQUEST_TIMEOUT', 120)
        if not self.timeout:
            raise MiddlewareNotUsed

    def __call__(self, request):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.get_response, request)
            try:
                response = future.result(timeout=self.timeout)
            except concurrent.futures.TimeoutError:
                response = HttpResponse("Request timed out", status=504)
            except Exception as e:
                response = HttpResponse(f"Request failed: {str(e)}", status=500)
        return response