from environ import Env
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from users.views import profile_view

env = Env()
Env.read_env()
ADMIN_PATH = env("ADMIN_PATH")

urlpatterns = [
    path("admin/", include("admin_honeypot.urls", namespace="admin_honeypot")),
    path(f"{ADMIN_PATH}/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("rtchat.urls")),
    path("profile/", include("users.urls")),
    path("@<username>/", profile_view, name="profile"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
