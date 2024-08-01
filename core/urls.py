from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from users.views import profile_view


urlpatterns = [
    path("admin/", include("admin_honeypot.urls", namespace="admin_honeypot")),
    path(f"91v9/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("rtchat.urls")),
    path("profile/", include("users.urls")),
    path("@<username>/", profile_view, name="profile"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
