import pytest
from django.contrib.auth import get_user_model
from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='password'
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        username='anotheruser',
        password='password'
    )


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def another_auth_client(client, another_user):
    client.force_login(another_user)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Test News',
        text='This is a test news item.'
    )


@pytest.fixture
def comment(db, user, news):
    return Comment.objects.create(
        news=news,
        author=user,
        text='This is a test comment.'
    )


@pytest.fixture
def forbidden_words():
    return ['badword1', 'badword2', 'badword3']
