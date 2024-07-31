from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .decorators import verified_required, chat_admin_required
from .forms import ChatMessageForm, NewGroupForm, ChatRoomEditForm
from .models import ChatGroup, GroupMessage


@login_required
@verified_required
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

    context = {
        "chat_messages": chat_messages,
        "form": form,
        "other_user": other_user,
        "chatroom_name": chatroom_name,
        "chat_group": chat_group,
    }
    return render(request, "rtchat/chat.html", context)


@login_required
@verified_required
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
@verified_required
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


@login_required
@verified_required
@chat_admin_required
def chatroom_edit_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    form = ChatRoomEditForm(instance=chat_group)
    if request.method == "POST":
        form = ChatRoomEditForm(request.POST, instance=chat_group)
        if form.is_valid:
            form.save()

            remove_members = request.POST.getlist("remove_members")
            for member_id in remove_members:
                member = get_object_or_404(User, id=member_id)
                chat_group.members.remove(member)

            return redirect("chatroom", chatroom_name)

    context = {
        "form": form,
        "chat_group": chat_group,
    }
    return render(request, "rtchat/chatroom_edit.html", context)


@login_required
@verified_required
@chat_admin_required
def chatroom_delete_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.method == "POST":
        chat_group_name = chat_group.groupchat_name
        chat_group.delete()
        msg = f"The chat group '{chat_group_name}' has been deleted."
        messages.success(request, msg)
        return redirect("home")

    context = {"chat_group": chat_group}
    return render(request, "rtchat/chatroom_delete.html", context)


@login_required
def chatroom_leave_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()

    if request.method == "POST":
        chat_group.members.remove(request.user)
        msg = "You have successfully left the chatroom."
        messages.success(request, msg)
        return redirect("home")


@login_required
@verified_required
@chat_admin_required
def chat_file_upload(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    if request.htmx and request.FILES:
        file = request.FILES["file"]
        message = GroupMessage.objects.create(
            file=file,
            author=request.user,
            group=chat_group,
        )
        channel_layers = get_channel_layer()
        event = {
            "type": "message_handler",
            "message_id": message.id,
        }
        async_to_sync(channel_layers.group_send)(chatroom_name, event)
    return HttpResponse()
