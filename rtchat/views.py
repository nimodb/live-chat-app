from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ChatMessageForm
from .models import ChatGroup


@login_required
def chat_view(request):
    chat_group = get_object_or_404(ChatGroup, group_name="public-chat")
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatMessageForm()

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

    context = {"chat_messages": chat_messages, "form": form}
    return render(request, "rtchat/chat.html", context)
