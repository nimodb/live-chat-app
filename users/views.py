from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from allauth.account.utils import send_email_confirmation
from .forms import ProfileForm, EmailForm


def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:
            profile = request.user.profile
        except:
            return redirect("account_login")
    context = {"profile": profile}
    return render(request, "users/profile.html", context)


@login_required
def profile_edit_view(request):
    form = ProfileForm(instance=request.user.profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid:
            form.save()
            return redirect("profile")

    if request.path == reverse("profile-onboarding"):
        onboarding = True
    else:
        onboarding = False

    context = {
        "form": form,
        "onboarding": onboarding,
    }
    return render(request, "users/profile_edit.html", context)


@login_required
def profile_settings_view(request):
    return render(request, "users/profile_settings.html")


@login_required
def profile_email_change(request):

    if request.htmx:
        form = EmailForm(instance=request.user)
        return render(request, "partials/email_form.html", {"form": form})

    if request.method == "POST":
        form = EmailForm(request.POST, instance=request.user)

        if form.is_valid():

            # Check if the email already exists
            email = form.cleaned_data["email"]
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.warning(request, f"{email} is already in use.")
                return redirect("profile-settings")

            form.save()
            # Then Signal updates email address and set verified to False

            # Then send confirmation email
            send_email_confirmation(request, request.user)
            messages.success(request, "Email address updated. Please check your inbox to verify the new email.")

            return redirect("profile-settings")
        else:
            messages.warning(request, "Form not valid")
            return redirect("profile-settings")

    return redirect("home")


@login_required
def profile_email_verify(request):
    send_email_confirmation(request, request.user)
    return redirect("profile-settings")


@login_required
def profile_delete_view(request):
    user = request.user
    if request.method == "POST":
        logout(request)
        user.delete()
        messages.success(request, "Account deleted, what a pity")
        return redirect("home")

    return render(request, "users/profile_delete.html")
