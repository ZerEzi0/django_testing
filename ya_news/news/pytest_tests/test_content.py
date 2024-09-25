import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from news.models import Comment
from django.conf import settings


@pytest.mark.django_db
def test_comments_are_sorted_by_oldest_first(client, news_item, user):
    """Проверяет, что комментарии сортируются от старых к новым."""
    # Создаём три комментария с разными датами создания
    comment1 = Comment.objects.create(
        news=news_item,
        author=user,
        text='Первый комментарий',
        created=timezone.now() - timedelta(hours=3)
    )
    comment2 = Comment.objects.create(
        news=news_item,
        author=user,
        text='Второй комментарий',
        created=timezone.now() - timedelta(hours=2)
    )
    comment3 = Comment.objects.create(
        news=news_item,
        author=user,
        text='Третий комментарий',
        created=timezone.now() - timedelta(hours=1)
    )
    url = reverse('news:detail', kwargs={'pk': news_item.pk})
    response = client.get(url)
    news_from_context = response.context.get('object')
    assert news_from_context is not None, "Новость не найдена в контексте"
    comments = news_from_context.comment_set.order_by('created')
    expected_comments = [comment1, comment2, comment3]
    assert list(comments) == expected_comments, (
        "Комментарии не отсортированы от старых к новым"
    )


@pytest.mark.django_db
def test_authenticated_user_can_see_comment_form(authorized_client, news_item):
    """Авторизованный пользователь видит форму для добавления комментария."""
    url = reverse('news:detail', kwargs={'pk': news_item.pk})
    response = authorized_client.get(url)
    assert 'form' in response.context, (
        "Форма для комментариев отсутствует в контексте"
    )
    form = response.context['form']
    assert form is not None, "Форма не передана в контекст"


@pytest.mark.django_db
def test_main_page_contains_no_more_than_news_count(
    client,
    many_news
):
    """
    Проверяет, что на главной странице 
    не более NEWS_COUNT_ON_HOME_PAGE новостей.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context.get('news_list')
    assert object_list is not None, (
        "Список новостей отсутствует в контексте"
    )
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE
    assert len(object_list) == news_count, (
        f"На странице должно быть не более {news_count} новостей"
    )


@pytest.mark.django_db
def test_news_are_sorted_by_date(client, many_news):
    """Проверяет, что новости отсортированы по дате от новых к старым."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context.get('news_list')
    assert object_list is not None, (
        "Список новостей отсутствует в контексте"
    )
    expected_order = sorted(
        many_news,
        key=lambda news: news.date,
        reverse=True
    )[:settings.NEWS_COUNT_ON_HOME_PAGE]
    assert list(object_list) == expected_order, (
        "Новости не отсортированы по дате от новых к старым"
    )
