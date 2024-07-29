from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ChatMessageForm
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

    context = {
        "chat_messages": chat_messages,
        "form": form,
        "other_user": other_user,
        "chatroom_name": chatroom_name,
        "user_chatrooms": user_chatrooms,
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
