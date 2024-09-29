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

    def test_home_page_accessible_to_anonymous(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_user_pages_accessible(self):
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_pages_accessible_only_to_author(self):

        note_slug = self.note.slug
        urls = (
            ('notes:detail', (note_slug,)),
            ('notes:edit', (note_slug,)),
            ('notes:delete', (note_slug,)),
        )

        for name, args in urls:
            with self.subTest(name=name, user='author'):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        for name, args in urls:
            with self.subTest(name=name, user='another_user'):
                url = reverse(name, args=args)
                response = self.another_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirects_for_anonymous_user(self):

        login_url = reverse('users:login')
        protected_urls = [
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        ]
        for name, args in protected_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                expected_redirect = f'{login_url}?next={url}'
                self.assertRedirects(response, expected_redirect)

    def test_public_pages_accessible_to_anonymous(self):

        urls = (
            ('users:signup', None),
            ('users:login', None),
            ('users:logout', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
