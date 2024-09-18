from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from djangosaml2.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chatbot1/', include('chatbot1.urls')),
    path('', include('chatbot1.urls')),
    path('api/v1/', include('chatbot1.urls')),
    path('saml2/', include('djangosaml2.urls')),
    path('saml2/login/', LoginView.as_view(), name='saml2_login'),
    path('saml2/logout/', LogoutView.as_view(), name='saml2_logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
