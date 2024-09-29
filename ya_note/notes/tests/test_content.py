from django.contrib.auth import get_user_model
from django.test import TestCase
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

    def setUp(self):
        self.client.force_login(self.user)

    def test_note_in_object_list(self):
        response = self.client.get(self.notes_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context)
        self.assertIn(self.user_note, response.context['object_list'])

    def test_notes_not_in_other_user_list(self):

        response = self.client.get(self.notes_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            self.another_user_note,
            response.context['object_list']
        )

    def test_forms_in_add_and_edit_pages(self):

        urls = (
            ('notes:add', None),
            ('notes:edit', (self.user_note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
