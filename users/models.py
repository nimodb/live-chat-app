from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="avatars/", null=True, blank=True)
    nickname = models.CharField(max_length=20, null=True, blank=True)
    info = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.user)

    @property
    def name(self):
        if self.nickname:
            return self.nickname
        return self.user.username

    @property
    def avatar(self):
        if self.image:
            return self.image.url
        return static("images/avatar.svg")