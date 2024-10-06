import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def user(db):
    """Создаёт пользователя с именем 'testuser'."""
    return User.objects.create_user(
        username='testuser',
        password='password'
    )


@pytest.fixture
def another_user(db):
    """Создаёт пользователя с именем 'anotheruser'."""
    return User.objects.create_user(
        username='anotheruser',
        password='password'
    )


@pytest.fixture
def author_client(client, user):
    """Клиент, залогиненный как 'testuser'."""
    client.force_login(user)
    return client


@pytest.fixture
def reader_client(client, another_user):
    """Клиент, залогиненный как 'anotheruser'."""
    client.force_login(another_user)
    return client


@pytest.fixture
def news(db):
    """Создаёт одну новость с заголовком 'Test News'."""
    return News.objects.create(
        title='Test News',
        text='This is a test news item.'
    )


@pytest.fixture
def comment(db, user, news):
    """Создаёт комментарий от 'testuser' к новости."""
    return Comment.objects.create(
        news=news,
        author=user,
        text='This is a test comment.'
    )


@pytest.fixture
def news_list(db):
    """
    Создаёт список новостей больше,
    чем NEWS_COUNT_ON_HOME_PAGE, с разными датами.
    """
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE + 5
    today = timezone.now()
    news_list = [
        News(
            title=f'News {i}',
            text='Some text',
            date=today - timedelta(days=i)
        )
        for i in range(news_count)
    ]
    News.objects.bulk_create(news_list)
    return news_list


@pytest.fixture
def comment_list(user, news):
    """Создаёт список комментариев к новости с разными датами."""
    now = timezone.now()
    comments = [
        Comment(
            news=news,
            author=user,
            text=f'Comment {i}',
            created=now - timedelta(minutes=i)
        )
        for i in range(10)
    ]
    Comment.objects.bulk_create(comments)
    return comments
