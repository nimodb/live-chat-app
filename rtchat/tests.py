from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from allauth.account.models import EmailAddress
from .models import ChatGroup


def create_user(username, verified=True):
    email = f"{username}@example.com"
    user = User.objects.create_user(username, email, "password")
    EmailAddress.objects.create(user=user, email=email, primary=True, verified=verified)
    return user


class ChatroomLeaveViewTests(TestCase):
    def setUp(self):
        self.admin = create_user("admin")
        self.member = create_user("member")
        self.group = ChatGroup.objects.create(groupchat_name="Group", admin=self.admin)
        self.group.members.add(self.admin, self.member)
        self.leave_url = reverse("chatroom-leave", args=[self.group.group_name])
        self.chat_url = reverse("chatroom", args=[self.group.group_name])

    def test_get_is_not_allowed(self):
        self.client.force_login(self.member)
        response = self.client.get(self.leave_url)
        self.assertEqual(response.status_code, 405)
        self.assertIn(self.member, self.group.members.all())

    # require_POST runs before login_required, so a GET is a 405 for everyone
    def test_anonymous_get_is_not_allowed(self):
        response = self.client.get(self.leave_url)
        self.assertEqual(response.status_code, 405)

    def test_anonymous_post_redirects_to_login(self):
        response = self.client.post(self.leave_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))
        self.assertIn(self.member, self.group.members.all())

    def test_member_can_leave(self):
        self.client.force_login(self.member)
        response = self.client.post(self.leave_url)
        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)
        self.assertNotIn(self.member, self.group.members.all())

    def test_admin_cannot_leave(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.leave_url)
        self.assertRedirects(response, self.chat_url, fetch_redirect_response=False)
        self.assertIn(self.admin, self.group.members.all())

    def test_unverified_user_cannot_leave(self):
        unverified = create_user("unverified", verified=False)
        self.group.members.add(unverified)
        self.client.force_login(unverified)
        response = self.client.post(self.leave_url)
        self.assertRedirects(
            response, reverse("profile-settings"), fetch_redirect_response=False
        )
        self.assertIn(unverified, self.group.members.all())

    def test_private_chat_cannot_be_left(self):
        private = ChatGroup.objects.create(is_private=True)
        private.members.add(self.admin, self.member)
        self.client.force_login(self.member)
        response = self.client.post(reverse("chatroom-leave", args=[private.group_name]))
        self.assertRedirects(
            response,
            reverse("chatroom", args=[private.group_name]),
            fetch_redirect_response=False,
        )
        self.assertEqual(private.members.count(), 2)

    def test_chat_page_links_to_leave_url_only_from_the_post_form(self):
        self.client.force_login(self.member)
        response = self.client.get(self.chat_url)
        self.assertContains(response, f'action="{self.leave_url}"', count=1)
        self.assertContains(response, self.leave_url, count=1)

    def test_chat_page_hides_leave_from_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.chat_url)
        self.assertNotContains(response, self.leave_url)

    def test_private_chat_page_hides_leave(self):
        private = ChatGroup.objects.create(is_private=True)
        private.members.add(self.admin, self.member)
        self.client.force_login(self.member)
        response = self.client.get(reverse("chatroom", args=[private.group_name]))
        self.assertNotContains(response, reverse("chatroom-leave", args=[private.group_name]))
