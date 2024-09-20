import threading
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse


class TimeoutException(Exception):
    pass


def timeout_handler(request, timeout):
    def _timeout():
        time.sleep(timeout)
        if not request.META.get('_timed_out', False):
            raise TimeoutException("Request timed out after {} seconds".format(timeout))

    thread = threading.Thread(target=_timeout)
    thread.setDaemon(True)
    thread.start()


class TimeoutMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timeout = 600  # 10 minutes in seconds
        timeout_handler(request, timeout)

        try:
            response = self.get_response(request)
        except TimeoutException:
            response = HttpResponse("Request Timeout", status=504)
        finally:
            request.META['_timed_out'] = True

        return response