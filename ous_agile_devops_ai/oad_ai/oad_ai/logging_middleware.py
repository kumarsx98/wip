# Create a file named logging_middleware.py
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class LoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.debug(f"Request URL: {request.get_full_path()}, Method: {request.method}")

    def process_response(self, request, response):
        logger.debug(f"Request URL: {request.get_full_path()}, Status Code: {response.status_code}")
        return response
