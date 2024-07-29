from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from .models import ChatGroup


def verified_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.emailaddress_set.filter(verified=True).exists():
            msg = "You need to be a verified user to access this feature. Please verify your account to continue."
            messages.warning(request, msg)
            return redirect("profile-settings")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def chat_admin_required(view_func):
    def _wrapped_view(request, chatroom_name, *args, **kwargs):
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
        if request.user != chat_group.admin:
            msg = "You are not authorized to edit this chatroom."
            messages.warning(request, msg)
            raise Http404("You are not authorized to edit this chatroom.")
        return view_func(request, chatroom_name, *args, **kwargs)

    return _wrapped_view
