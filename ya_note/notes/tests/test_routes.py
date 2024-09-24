import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note


@pytest.mark.django_db
class YaNoteRoutesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password2'
        )
        self.note1 = Note.objects.create(
            title="User1's Note",
            text="Text for user1",
            slug="user1-note",
            author=self.user1
        )

    def test_anonymous_user_redirected_to_login(self):
        restricted_urls = [
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:success'),
            reverse('notes:detail', kwargs={'slug': self.note1.slug}),
        ]

        for url in restricted_urls:
            response = self.client.get(url)
            print(response.url)
            self.assertRedirects(response, f'/auth/login/?next={url}')
