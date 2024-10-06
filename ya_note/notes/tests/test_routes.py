from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author',
            password='pass'
        )
        cls.another_user = User.objects.create_user(
            username='another_user',
            password='pass'
        )

        cls.note = Note.objects.create(
            title='Test Note',
            text='Note text',
            slug='test-note',
            author=cls.author
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.another_client = Client()
        cls.another_client.force_login(cls.another_user)

    def test_authorized_user_pages_accessible(self):
        """Тест на доступность страниц для авторизованного пользователя."""
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_accessible_only_to_author(self):
        """Тест на доступность страниц заметки только для автора."""
        note_slug = self.note.slug
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        clients_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.another_client, HTTPStatus.NOT_FOUND),
        )
        for client, status in clients_statuses:
            for name in urls:
                with self.subTest(name=name, client=client):
                    url = reverse(name, args=(note_slug,))
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_anonymous_user(self):
        """Тест на переадресацию незалогиненного пользователя."""
        login_url = reverse('users:login')
        note_slug = self.note.slug
        protected_urls = [
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (note_slug,)),
            ('notes:edit', (note_slug,)),
            ('notes:delete', (note_slug,)),
        ]
        for name, args in protected_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                expected_redirect = f'{login_url}?next={url}'
                self.assertRedirects(response, expected_redirect)

    def test_public_pages_accessible_to_anonymous(self):
        """
        Тест на доступность публичных
        страниц для анонимных пользователей.
        """
        urls = (
            'notes:home',
            'users:signup',
            'users:login',
            'users:logout',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
