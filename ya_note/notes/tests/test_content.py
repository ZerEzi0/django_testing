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

        cls.note = Note.objects.create(
            title='User Note',
            text='User note text',
            slug='user-note',
            author=cls.user
        )

        cls.notes_list_url = reverse('notes:list')

        # Создаём клиентов для каждого пользователя
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)

    def test_notes_in_object_list(self):
        """Тест на отображение заметки в списке заметок."""
        test_cases = (
            (self.user_client, True),
            (self.another_user_client, False),
        )
        for client, expected in test_cases:
            with self.subTest(client=client):
                response = client.get(self.notes_list_url)
                object_list = response.context.get('object_list', [])
                result = self.note in object_list
                self.assertIs(result, expected)

    def test_forms_in_add_and_edit_pages(self):
        """
        Тест наличия формы на страницах
        добавления и редактирования заметки.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.user_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
