import pytest
from django.contrib.auth.models import User
from django.test import Client

from notes.models import Note


@pytest.fixture
def author(db):
    """Создаёт пользователя-автора."""
    return User.objects.create_user(
        username='author',
        password='password123'
    )


@pytest.fixture
def another_user(db):
    """Создаёт другого пользователя."""
    return User.objects.create_user(
        username='anotheruser',
        password='password456'
    )


@pytest.fixture
def client():
    """Клиент для неавторизованного пользователя."""
    return Client()


@pytest.fixture
def author_client(author):
    """Клиент с авторизованным автором."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def another_user_client(another_user):
    """Клиент с авторизованным другим пользователем."""
    client = Client()
    client.force_login(another_user)
    return client


@pytest.fixture
def note(author):
    """Создаёт заметку, принадлежащую автору."""
    return Note.objects.create(
        title="User's Note",
        text="Text for user's note",
        slug="user-note",
        author=author
    )


@pytest.fixture
def note_form_data():
    """Данные формы для создания заметки."""
    return {
        'title': 'Test Note',
        'text': 'Test note text',
        'slug': 'test-note',
    }


@pytest.fixture
def note_form_data_without_slug():
    """Данные формы для создания заметки без указания slug."""
    return {
        'title': 'Automatic Slug',
        'text': 'Text',
    }
