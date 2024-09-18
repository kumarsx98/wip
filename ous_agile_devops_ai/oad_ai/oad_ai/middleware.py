from django.utils.deprecation import MiddlewareMixin


class XFrameOptionsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Allow iframes for the media files
        if request.path.startswith('/media/'):
            response['X-Frame-Options'] = 'ALLOWALL'
        return response
