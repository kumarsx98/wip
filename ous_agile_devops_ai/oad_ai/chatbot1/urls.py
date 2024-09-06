# urls.py

from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from djangosaml2.views import LoginView
from djangosaml2 import views as saml2_views


urlpatterns = [
    path('search/', views.api_search, name='api_search'),
    path('', views.search, name='search'),
    path('create-source/', views.create_source, name='create_source'),
    path('sync-source/<str:source>/', views.sync_source, name='sync_source'),

    path('list-sources/', views.list_sources, name='list_sources'),
    path('list-documents/<str:source>/', views.list_documents, name='list_documents'),

    path('view-document-content/<str:source>/<str:document_id>/', views.view_document_content, name='view_document_content'),
    path('auto-upload/', views.auto_upload, name='auto_upload'),
    path('get-upload-status/', views.get_upload_status_view, name='get_upload_status'),
    path('start-scheduler/', views.start_scheduler_view, name='start_scheduler'),
    path('user-info/', views.user_info, name='user_info'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/current-user/', views.current_user, name='current_user'),
    path('saml2/login/', LoginView.as_view(), name='saml2_login'),
    path('saml2/acs/', views.CustomAssertionConsumerServiceView.as_view(), name='saml2_acs'),
    path('saml2/metadata/', views.sp_metadata, name='saml2_metadata'),
    #path('saml2/metadata/', saml2_views.metadata, name='saml2_metadata'),
    path('list-sources/', views.list_sources, name='list_sources'),
    path('list-documents/<str:source>/', views.list_documents, name='list_documents'),
    path('upload-document/<str:source>/', views.upload_document, name='upload_document'),
    path('check-upload-status/<str:source>/<str:task_id>/', views.check_upload_status, name='check_upload_status'),

    path('', views.index, name='index'),
]