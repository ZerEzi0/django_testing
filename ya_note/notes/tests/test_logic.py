import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note


@pytest.mark.django_db
class YaNoteLogicTestCase(TestCase):
    def setUp(self):
        self.client = self.client
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

    def test_cannot_create_note_with_duplicate_slug(self):
        self.client.login(
            username='user1',
            password='password1'
        )
        response = self.client.post(
            reverse(
                'notes:add'
            ), 
            {
                'title': 'Duplicate Slug Note',
                'text': 'Text',
                'slug': 'user1-note'
            }
        )
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, "Заметка с таким Slug уже существует.")
