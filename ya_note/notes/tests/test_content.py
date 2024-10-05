from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user', password='pass')
        cls.another_user = User.objects.create_user(
            username='another_user',
            password='pass'
        )

        cls.user_note = Note.objects.create(
            title='User Note',
            text='User note text',
            slug='user-note',
            author=cls.user
        )

        cls.another_user_note = Note.objects.create(
            title='Another User Note',
            text='Another user note text',
            slug='another-user-note',
            author=cls.another_user
        )

        cls.notes_list_url = reverse('notes:list')

        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)

    def test_notes_in_object_list(self):
        """Тест на верное отображение."""
        test_cases = (
            (self.user_client, self.user_note, True),
            (self.user_client, self.another_user_note, False),
            (self.another_user_client, self.another_user_note, True),
            (self.another_user_client, self.user_note, False),
        )
        for client, note, expected in test_cases:
            with self.subTest(client=client, note=note):
                response = client.get(self.notes_list_url)
                object_list = response.context.get('object_list', [])
                result = note in object_list
                self.assertIs(result, expected)

    def test_forms_in_add_and_edit_pages(self):
        """Тест на добавление и редактирование страниц."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.user_note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.user_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
