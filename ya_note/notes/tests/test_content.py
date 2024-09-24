import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note
from notes.forms import NoteForm

@pytest.mark.django_db
class YaNoteContentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1', password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2', password='password2'
        )
        self.note1 = Note.objects.create(
            title="User1's Note", text="Text for user1",
            slug="user1-note", author=self.user1
        )
        self.note2 = Note.objects.create(
            title="User2's Note", text="Text for user2",
            slug="user2-note", author=self.user2
        )

    def test_note_in_object_list(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.note1, response.context['object_list'])
        self.assertNotIn(self.note2, response.context['object_list'])

    def test_note_form_in_creation_and_edit_pages(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], NoteForm)

        response = self.client.get(reverse('notes:edit', kwargs={
            'slug': self.note1.slug
        }))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], NoteForm)
