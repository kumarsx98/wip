from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from djangosaml2.views import LoginView

urlpatterns = [
    #path('search/', views.api_search, name='api_search'),
    path('saml2/login/', views.custom_login, name='saml2_login'),
    path('', views.search, name='search'),
    path('create-source/', views.create_source, name='create_source'),
    path('upload_document/<str:source>/', views.upload_document, name='upload_document'),
    path('check-upload-status/<str:source>/<str:task_id>/', views.check_upload_status_view, name='check_upload_status'),

    path('sync-source/<str:source>/', views.sync_source, name='sync_source'),
    path('list-sources/', views.list_sources, name='list_sources'),
    path('list-documents/<str:source>/', views.list_documents, name='list_documents'),
    path('user-info/', views.user_info, name='user_info'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('saml2/login/', LoginView.as_view(), name='saml2_login'),
    path('saml2/metadata/', views.sp_metadata, name='saml2_metadata'),
    path('check-upload-status/<str:source>/<str:task_id>/', views.check_upload_status, name='check_upload_status'),
    path('trigger-auto-upload/', views.trigger_auto_upload, name='trigger-auto-upload'),
    path('get-upload-status/', views.get_upload_status, name='get-upload-status'),
    path('api/v1/sources/<str:source>/delete/', views.delete_source, name='delete_source'),  # Correct endpoint
    #path('api/search/', views.api_search, name='api_search'),
    path('delete-document/<str:source>/<str:document_id>/', views.delete_document, name='delete_document'),
    path('chat-with-source/<str:source_name>/', views.chat_with_source, name='chat-with-source'),
    path('saml2/session/', views.session_status, name='session_status'),
    path('saml2/logout/', views.custom_logout, name='saml2_logout'),
    path('get-user-token/', views.get_user_token, name='get_user_token'),
    path('delete-source/<str:source>/', views.delete_source, name='delete_source'),
    #path('delete-source/<str:source>/', views.delete_source, name='delete_source'),

]
