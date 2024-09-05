# chatbot1/saml_views.py

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect

@login_required
def saml_login_complete(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    return JsonResponse({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

@login_required
def index(request):
    return HttpResponse("Welcome, {}".format(request.user.username))