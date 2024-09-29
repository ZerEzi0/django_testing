from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

from pytils.translit import slugify

User = get_user_model()


class TestNoteLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user', password='pass')
        cls.another_user = User.objects.create_user(
            username='another_user',
            password='pass'
        )

        cls.note = Note.objects.create(
            title='Existing Note',
            text='Existing note text',
            slug='existing-note',
            author=cls.user
        )

        cls.another_note = Note.objects.create(
            title='Another User Note',
            text='Another user note text',
            slug='another-user-note',
            author=cls.another_user
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.note_data = {
            'title': 'Test Note',
            'text': 'Note text',
            'slug': 'test-note',
        }

    def test_logged_in_user_can_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.client.post(reverse('notes:add'), data=self.note_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        note = Note.objects.get(slug=self.note_data['slug'])
        self.assertEqual(note.title, self.note_data['title'])
        self.assertEqual(note.text, self.note_data['text'])
        self.assertEqual(note.author, self.user)

    def test_anonymous_user_cannot_create_note(self):
        self.client.logout()
        notes_count_before = Note.objects.count()
        response = self.client.post(reverse('notes:add'), data=self.note_data)
        self.assertEqual(Note.objects.count(), notes_count_before)
        login_url = reverse('users:login')
        expected_redirect = f'{login_url}?next={reverse("notes:add")}'
        self.assertRedirects(response, expected_redirect)

    def test_cannot_create_note_with_existing_slug(self):
        duplicate_data = {
            'title': 'Duplicate Note',
            'text': 'Duplicate note text',
            'slug': self.note.slug,
        }
        notes_count_before = Note.objects.count()
        response = self.client.post(reverse('notes:add'), data=duplicate_data)
        self.assertEqual(Note.objects.count(), notes_count_before)
        self.assertEqual(response.status_code, 200)
        expected_error = (
            f'{self.note.slug} - такой slug уже существует, '
            f'придумайте уникальное значение!'
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=expected_error
        )

    def test_slug_is_generated_if_not_provided(self):
        data_without_slug = {'title': 'Новая заметка', 'text': 'Текст заметки'}
        notes_count_before = Note.objects.count()
        response = self.client.post(
            reverse('notes:add'),
            data=data_without_slug
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        note = Note.objects.get(title='Новая заметка')
        expected_slug = slugify(data_without_slug['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_user_can_edit_own_note(self):
        new_data = {
            'title': 'Updated Title',
            'text': 'Updated text',
            'slug': self.note.slug,
        }
        response = self.client.post(
            reverse('notes:edit', args=(self.note.slug,)), data=new_data
        )
        self.note.refresh_from_db()
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(self.note.title, new_data['title'])
        self.assertEqual(self.note.text, new_data['text'])

    def test_user_cannot_edit_others_note(self):
        new_data = {
            'title': 'Hacked Title',
            'text': 'Hacked text',
            'slug': self.another_note.slug,
        }
        response = self.client.post(
            reverse(
                'notes:edit',
                args=(self.another_note.slug,)), data=new_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.another_note.refresh_from_db()
        self.assertNotEqual(self.another_note.title, new_data['title'])

    def test_user_can_delete_own_note(self):
        response = self.client.post(
            reverse('notes:delete', args=(self.note.slug,)), follow=True
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertFalse(Note.objects.filter(slug=self.note.slug).exists())

    def test_user_cannot_delete_others_note(self):
        response = self.client.post(
            reverse('notes:delete', args=(self.another_note.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(
            Note.objects.filter(
                slug=self.another_note.slug
            ).exists()
        )
