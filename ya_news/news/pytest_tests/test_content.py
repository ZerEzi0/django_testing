import pytest
from django.urls import reverse
from django.conf import settings
from pytest_lazyfixture import lazy_fixture

from news.models import News, Comment
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.fixture
def news_list(db):
    """
    Создаёт список новостей в соответствии
    с настройкой NEWS_COUNT_ON_HOME_PAGE.
    """
    num_news = settings.NEWS_COUNT_ON_HOME_PAGE
    return News.objects.bulk_create([
        News(title=f'News {i}', text='Some text') for i in range(num_news)
    ])


@pytest.fixture
def comment_list(db, user, news):
    """Создаёт список комментариев в определённом порядке."""
    comment_old = Comment.objects.create(
        news=news,
        author=user,
        text='First comment'
    )
    comment_new = Comment.objects.create(
        news=news,
        author=user,
        text='Second comment'
    )
    return [comment_old, comment_new]


def test_news_order_ascending_on_homepage(client, news_list):
    """
    Проверяет, что на главной странице новости
    отображаются в порядке от самых старых к самым новым.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    expected_order = list(
        News.objects.all().order_by(
            'date'
        )[:settings.NEWS_COUNT_ON_HOME_PAGE]
    )
    assert list(object_list) == expected_order


def test_news_order_descending_on_homepage(client, news_list):
    """
    Проверяет, что на главной странице новости
    отображаются в порядке от самых свежих к самым старым.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    expected_order = list(
        News.objects.all().order_by(
            '-date'
        )[:settings.NEWS_COUNT_ON_HOME_PAGE]
    )
    assert list(object_list) == expected_order


def test_comments_order_on_news_detail(client, news, comment_list):
    """
    Проверяет, что комментарии к новости
    отображаются в порядке от старых к новым.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    news_in_context = response.context['object']
    comments_in_context = news_in_context.comment_set.all()
    expected_order = sorted(comment_list, key=lambda c: c.id)
    assert list(comments_in_context) == expected_order


@pytest.mark.parametrize('client_fixture, form_expected', [
    (lazy_fixture('reader_client'), True),
    (lazy_fixture('author_client'), True),
])
def test_comment_form_visibility(client_fixture, form_expected, news):
    """
    Проверяет видимость формы добавления комментария:
    - Видна для всех авторизованных пользователей.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client_fixture.get(url)
    has_form = 'form' in response.context
    assert has_form == form_expected
    if has_form:
        assert isinstance(response.context['form'], CommentForm)
