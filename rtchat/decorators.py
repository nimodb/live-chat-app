from django.shortcuts import redirect
from django.contrib import messages


def verified_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.emailaddress_set.filter(verified=True).exists():
            print("not")
            msg = "You need to be a verified user to access this feature. Please verify your account to continue."
            messages.warning(request, msg)
            return redirect("profile-settings")
        print("yes")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
