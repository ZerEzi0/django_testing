import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_on_homepage(client, news_list, news_home_url):
    """
    Проверяет, что на главной странице не более
    NEWS_COUNT_ON_HOME_PAGE новостей.
    """
    response = client.get(news_home_url)
    object_list = response.context.get('object_list')
    assert object_list is not None, 'В контексте отсутствует object_list'
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE, (
        'Должно отображаться не более '
        f'{settings.NEWS_COUNT_ON_HOME_PAGE} новостей'
    )


def test_news_order_on_homepage(client, news_list, news_home_url):
    """Проверяет порядок новостей на главной странице от новых к старым."""
    response = client.get(news_home_url)
    object_list = response.context.get('object_list')
    assert object_list is not None, 'В контексте отсутствует object_list'

    news_dates = [news.date for news in object_list]
    sorted_dates = sorted(news_dates, reverse=True)
    assert news_dates == sorted_dates, (
        'Новости отображаются не в порядке от новых к старым'
    )


def test_comments_order_on_news_detail(client, news_detail_url, comment_list):
    """Проверяет, что комментарии отображаются в порядке от старых к новым."""
    response = client.get(news_detail_url)
    news_in_context = response.context.get('object')
    assert news_in_context is not None, (
        'В контексте отсутствует объект новости'
    )
    comments_in_context = news_in_context.comment_set.all()
    comments_dates = [comment.created for comment in comments_in_context]
    sorted_dates = sorted(comments_dates)
    assert comments_dates == sorted_dates, (
        'Комментарии отображаются не в порядке от старых к новым'
    )


@pytest.mark.parametrize('client_fixture, form_expected', [
    (pytest.lazy_fixture('client'), False),
    (pytest.lazy_fixture('author_client'), True),
])
def test_comment_form_visibility(
    client_fixture,
    form_expected,
    news_detail_url
):
    """Проверяет видимость формы добавления комментария."""
    response = client_fixture.get(news_detail_url)
    has_form = 'form' in response.context
    assert has_form == form_expected
    if has_form:
        assert isinstance(response.context['form'], CommentForm)
