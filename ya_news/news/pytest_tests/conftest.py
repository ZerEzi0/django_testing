import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def user(db):
    """Создаёт пользователя."""
    user = User.objects.create_user(
        username='testuser',
        password='password123'
    )
    return user


@pytest.fixture
def another_user(db):
    """Создаёт другого пользователя."""
    another_user = User.objects.create_user(
        username='anotheruser',
        password='password456'
    )
    return another_user


@pytest.fixture
def client():
    """Клиент для неавторизованного пользователя."""
    return Client()


@pytest.fixture
def authorized_client(user):
    """Клиент с авторизованным пользователем."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def another_authorized_client(another_user):
    """Клиент с авторизованным другим пользователем."""
    client = Client()
    client.force_login(another_user)
    return client


@pytest.fixture
def news_item(db):
    """Создаёт объект новости."""
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
        date=timezone.now()
    )
    return news


@pytest.fixture
def comment(db, news_item, user):
    """Создаёт комментарий к новости от пользователя."""
    comment = Comment.objects.create(
        news=news_item,
        author=user,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comment_from_another_user(db, news_item, another_user):
    """Создаёт комментарий к новости от другого пользователя."""
    comment = Comment.objects.create(
        news=news_item,
        author=another_user,
        text='Комментарий от другого пользователя'
    )
    return comment


@pytest.fixture
def many_news(db):
    """Создаёт много новостей для проверки ограничения на главной странице."""
    news_list = []
    for i in range(15):  # Предположим, что NEWS_COUNT_ON_HOME_PAGE = 10
        news = News.objects.create(
            title=f'Новость {i}',
            text='Текст новости',
            date=timezone.now() - timezone.timedelta(days=i)
        )
        news_list.append(news)
    return news_list
