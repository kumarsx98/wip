# Insert debug statements in middleware
class SamlSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Processing request: {request.method} {request.get_full_path()}")
        response = self.get_response(request)
        print(f"Processed response: {response.status_code} {response.content[:100]}")
        return response
