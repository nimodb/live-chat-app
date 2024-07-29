from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ChatMessageForm, NewGroupForm
from .models import ChatGroup


@login_required
def chat_view(request, chatroom_name="public-chat"):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatMessageForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        other_user = chat_group.members.exclude(pk=request.user.pk).first()

    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            chat_group.members.add(request.user)

    if request.htmx:
        form = ChatMessageForm(request.POST)
        if form.is_valid:
            user = request.user
            message = form.save(commit=False)
            message.author = user
            message.group = chat_group
            message.save()
            context_hx = {"message": message, "user": user}
            return render(request, "rtchat/partials/chat_message_p.html", context_hx)

    user_chatrooms = request.user.chat_groups.filter(is_private=True)
    user_chatgroups = request.user.chat_groups.all()

    context = {
        "chat_messages": chat_messages,
        "form": form,
        "other_user": other_user,
        "chatroom_name": chatroom_name,
        "chat_group": chat_group,
        "user_chatrooms": user_chatrooms,
        "user_chatgroups": user_chatgroups,
    }
    return render(request, "rtchat/chat.html", context)


@login_required
def get_or_create_chatroom(request, username):
    if request.user == username:
        return redirect("home")

    other_user = get_object_or_404(User, username=username)

    chatroom = request.user.chat_groups.filter(
        is_private=True, members=other_user
    ).first()

    if not chatroom:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user, request.user)

    return redirect("chatroom", chatroom.group_name)


@login_required
def create_groupchat(request):
    form = NewGroupForm()

    if request.method == "POST":
        form = NewGroupForm(request.POST)
        if form.is_valid:
            new_groupname = form.save(commit=False)
            new_groupname.admin = request.user
            new_groupname.save()
            new_groupname.members.add(request.user)
            return redirect("chatroom", new_groupname.group_name)

    context = {
        "form": form,
    }
    return render(request, "rtchat/create_groupchat.html", context)
