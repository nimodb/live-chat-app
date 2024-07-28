from django.urls import path
from .views import *

urlpatterns = [
    path("", profile_view, name="profile"),
    path("edit/", profile_edit_view, name="profile-edit"),
    path("onboarding/", profile_edit_view, name="profile-onboarding"),
    path("setting/", profile_settings_view, name="profile-settings"),
    path("email-change/", profile_email_change, name="profile-email-change"),
    path("email-verify/", profile_email_verify, name="profile-email-verify"),
    path("delete/", profile_delete_view, name="profile-delete"),
]
