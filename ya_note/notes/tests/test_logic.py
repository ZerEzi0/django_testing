import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note
from pytils.translit import slugify


@pytest.mark.django_db
class YaNoteLogicTestCase(TestCase):
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

    def test_authenticated_user_can_create_note(self):
        self.client.login(
            username='user1',
            password='password1'
        )
        response = self.client.post(
            reverse(
                'notes:add'
                ),{'title': 'New Note', 'text': 'Text for new note'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(title='New Note').exists())

    def test_anonymous_user_cannot_create_note(self):
        response = self.client.post(
            reverse(
                'notes:add'
                ),{'title': 'Anonymous Note', 'text': 'Text for anonymous note'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login/?next=/notes/add/')

    def test_cannot_create_note_with_duplicate_slug(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(reverse('notes:add'), {
            'title': 'Duplicate Slug Note',
            'text': 'Text', 'slug': 'user1-note'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заметка с таким Slug уже существует.")

    def test_slug_is_generated_if_not_provided(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(reverse('notes:add'), {
            'title': 'Automatic Slug', 'text': 'Text'
        })
        self.assertEqual(response.status_code, 302)
        note = Note.objects.get(title='Automatic Slug')
        self.assertEqual(note.slug, slugify('Automatic Slug'))

    def test_user_can_edit_own_note(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(
            reverse(
                'notes:edit', kwargs={'slug': self.note1.slug}
            ), {'title': 'Edited Note', 'text': 'Edited Text'}
        )
        self.assertEqual(response.status_code, 302)
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, 'Edited Note')

    def test_user_cannot_edit_another_user_note(self):
        self.client.login(username='user2', password='password2')
        response = self.client.post(
            reverse(
                'notes:edit',
                kwargs={'slug': self.note1.slug}
            ), {'title': 'Edited by User2', 'text': 'Edited Text'}
        )
        self.assertEqual(response.status_code, 404)

    def test_user_can_delete_own_note(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(
            reverse(
                'notes:delete',
                kwargs={'slug': self.note1.slug}
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(slug='user1-note').exists())

    def test_user_cannot_delete_another_user_note(self):
        self.client.login(username='user2', password='password2')
        response = self.client.post(
            reverse(
                'notes:delete',
                kwargs={'slug': self.note1.slug}
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(slug='user1-note').exists())
