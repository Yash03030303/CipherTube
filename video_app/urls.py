from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views
from streamers import views as streamers_views

from stream.views import serve_secure_media


urlpatterns = [
    path('admin/', admin.site.urls), 
    path('',include('stream.urls')),
    path('profile',streamers_views.profile, name="profile"),
    path('register/',streamers_views.register, name="register"),
    path('login', auth_views.LoginView.as_view(template_name='streamers/login.html'), name="login"),
    path('logout',auth_views.LogoutView.as_view(template_name='streamers/logout.html'), name="logout"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SERVE_MEDIA_SECURELY:
    urlpatterns += [
        path(f'{settings.MEDIA_URL.strip("/")}/<path:path>', serve_secure_media),
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
