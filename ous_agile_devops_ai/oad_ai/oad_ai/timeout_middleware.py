import signal

class TimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def handler(signum, frame):
            raise Exception("Request took too long")

        # Change the timeout value here
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(600)  # 600 seconds = 10 minutes

        response = self.get_response(request)

        signal.alarm(0)  # Disable the alarm after the request is served
        return response
