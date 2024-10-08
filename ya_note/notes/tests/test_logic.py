from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user', password='pass')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.another_user = User.objects.create_user(
            username='another_user',
            password='pass'
        )
        cls.another_client = Client()
        cls.another_client.force_login(cls.another_user)

        cls.note_data = {
            'title': 'Test Note',
            'text': 'Note text',
            'slug': 'test-note',
        }

        cls.note = Note.objects.create(
            title='Existing Note',
            text='Existing note text',
            slug='existing-note',
            author=cls.user
        )

        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.url_login = reverse('users:login')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))

    def test_logged_in_user_can_create_note(self):
        """Проверка, может ли пользователь создать заметку."""
        notes_count_before = Note.objects.count()
        response = self.authorized_client.post(
            self.url_add,
            data=self.note_data
        )
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        note = Note.objects.exclude(pk=self.note.pk).get()
        self.assertEqual(note.title, self.note_data['title'])
        self.assertEqual(note.text, self.note_data['text'])
        self.assertEqual(note.slug, self.note_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_anonymous_user_cannot_create_note(self):
        """Тест, что анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()
        response = self.client.post(self.url_add, data=self.note_data)
        self.assertEqual(Note.objects.count(), notes_count_before)
        expected_redirect = f'{self.url_login}?next={self.url_add}'
        self.assertRedirects(response, expected_redirect)

    def test_cannot_create_note_with_existing_slug(self):
        """Тест на создание заметки с уже существующим slug."""
        data_with_existing_slug = self.note_data.copy()
        data_with_existing_slug['slug'] = self.note.slug
        notes_count_before = Note.objects.count()
        response = self.authorized_client.post(
            self.url_add,
            data=data_with_existing_slug
        )
        self.assertEqual(Note.objects.count(), notes_count_before)
        expected_error = self.note.slug + WARNING
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=expected_error
        )

    def test_slug_is_generated_if_not_provided(self):
        """Тест на автоматическую генерацию slug."""
        data_without_slug = self.note_data.copy()
        data_without_slug.pop('slug')
        notes_count_before = Note.objects.count()
        response = self.authorized_client.post(
            self.url_add,
            data=data_without_slug
        )
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        note = Note.objects.exclude(pk=self.note.pk).get()
        expected_slug = slugify(data_without_slug['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_user_can_edit_own_note(self):
        """Тест на изменение собственной заметки пользователем."""
        response = self.authorized_client.post(
            self.url_edit,
            data=self.note_data
        )
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.note_data['title'])
        self.assertEqual(self.note.text, self.note_data['text'])
        self.assertEqual(self.note.slug, self.note_data['slug'])

    def test_user_cannot_edit_others_note(self):
        """Тест на изменение заметки другим пользователем."""
        response = self.another_client.post(self.url_edit, data=self.note_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_after = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note_after.title, self.note.title)
        self.assertEqual(note_after.text, self.note.text)
        self.assertEqual(note_after.slug, self.note.slug)

    def test_user_can_delete_own_note(self):
        """Тест, что пользователь может удалить свою заметку."""
        notes_count_before = Note.objects.count()
        response = self.authorized_client.post(self.url_delete)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), notes_count_before - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_user_cannot_delete_others_note(self):
        """
        Тест на то, что пользователь
        не может удалить заметку другого пользователя.
        """
        response = self.another_client.post(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
