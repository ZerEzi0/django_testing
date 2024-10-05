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
        """TПроверка, может ли пользователь создать заметку."""
        notes_count_before = Note.objects.count()
        response = self.authorized_client.post(
            self.url_add,
            data=self.note_data
        )
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        note = Note.objects.exclude(pk=self.note.pk).latest('id')
        self.assertEqual(note.title, self.note_data['title'])
        self.assertEqual(note.text, self.note_data['text'])
        self.assertEqual(note.slug, self.note_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_anonymous_user_cannot_create_note(self):
        """Test that an anonymous user cannot create a note."""
        anonymous_client = Client()
        notes_count_before = Note.objects.count()
        response = anonymous_client.post(self.url_add, data=self.note_data)
        self.assertEqual(Note.objects.count(), notes_count_before)
        expected_redirect = f'{self.url_login}?next={self.url_add}'
        self.assertRedirects(response, expected_redirect)

    def test_cannot_create_note_with_existing_slug(self):
        """Тест на заметку со slug."""
        duplicate_data = self.note_data.copy()
        duplicate_data['slug'] = self.note.slug
        notes_count_before = Note.objects.count()
        response = self.authorized_client.post(
            self.url_add,
            data=duplicate_data
        )
        self.assertEqual(Note.objects.count(), notes_count_before)
        expected_error = duplicate_data['slug'] + WARNING
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=expected_error
        )

    def test_slug_is_generated_if_not_provided(self):
        """Тест на генерацию slug."""
        data_without_slug = self.note_data.copy()
        del data_without_slug['slug']
        data_without_slug['title'] = 'Новая заметка'
        data_without_slug['text'] = 'Текст заметки'
        notes_count_before = Note.objects.count()
        response = self.authorized_client.post(
            self.url_add,
            data=data_without_slug
        )
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        note = Note.objects.exclude(pk=self.note.pk).latest('id')
        expected_slug = slugify(data_without_slug['title'])[:100]
        self.assertEqual(note.slug, expected_slug)

    def test_user_can_edit_own_note(self):
        """Тест на изменение заметки."""
        new_data = self.note_data.copy()
        new_data['title'] = 'Updated Title'
        new_data['text'] = 'Updated text'
        new_data['slug'] = 'updated-slug'
        response = self.authorized_client.post(self.url_edit, data=new_data)
        self.assertRedirects(response, self.url_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, new_data['title'])
        self.assertEqual(self.note.text, new_data['text'])
        self.assertEqual(self.note.slug, new_data['slug'])

    def test_user_cannot_edit_others_note(self):
        """Тест на изменение заметки другим пользователем."""
        another_user = User.objects.create_user(
            username='another_user',
            password='pass'
        )
        another_note = Note.objects.create(
            title='Another Note',
            text='Another note text',
            slug='another-note',
            author=another_user
        )
        url_edit_another = reverse('notes:edit', args=(another_note.slug,))
        new_data = self.note_data.copy()
        new_data['title'] = 'Hacked Title'
        new_data['text'] = 'Hacked text'
        new_data['slug'] = 'hacked-slug'
        response = self.authorized_client.post(url_edit_another, data=new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_after = Note.objects.get(pk=another_note.pk)
        self.assertEqual(note_after.title, 'Another Note')
        self.assertEqual(note_after.text, 'Another note text')
        self.assertEqual(note_after.slug, 'another-note')

    def test_user_can_delete_own_note(self):
        """Тест, что пользователь может удалить свою же заметку."""
        notes_count_before = Note.objects.count()
        response = self.authorized_client.post(self.url_delete)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(Note.objects.count(), notes_count_before - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_user_cannot_delete_others_note(self):
        """
        Тест на то, что пользователь не может
        удалить заметку  другого пользователя.
        """
        another_user = User.objects.create_user(
            username='another_user',
            password='pass'
        )
        another_note = Note.objects.create(
            title='Another Note',
            text='Another note text',
            slug='another-note',
            author=another_user
        )
        notes_count_before = Note.objects.count()
        url_delete_another = reverse('notes:delete', args=(another_note.slug,))
        response = self.authorized_client.post(url_delete_another)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before)
        self.assertTrue(Note.objects.filter(pk=another_note.pk).exists())
