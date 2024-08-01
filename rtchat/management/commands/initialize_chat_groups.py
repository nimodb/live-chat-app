from django.core.management.base import BaseCommand
from rtchat.models import ChatGroup


class Command(BaseCommand):
    help = "Initialize default chat groups"

    def handle(self, *args, **kwargs):
        group_names = ["public-chat", "online-status"]
        existing_groups = []
        new_groups = []

        for name in group_names:
            chat_group, created = ChatGroup.objects.get_or_create(group_name=name)
            if created:
                new_groups.append(name)
            else:
                existing_groups.append(name)

        if new_groups:
            new_groups = ", ".join(new_groups)
            msg = f"Successfully created default chat groups: {new_groups}"
            self.stdout.write(self.style.SUCCESS(msg))

        if existing_groups:
            existing_groups = ", ".join(existing_groups)
            msg = f"The following chat groups already exist: {existing_groups}"
            self.stderr.write(self.style.WARNING(msg))
