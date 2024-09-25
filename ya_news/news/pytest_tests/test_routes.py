import pytest
from django.urls import reverse
from http import HTTPStatus

from news.models import Comment


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', [
    'news:home',
    'users:login',
    'users:logout',
    'users:signup',
])
def test_pages_accessible_by_anonymous_user(client, url_name):
    """Страницы доступны анонимному пользователю."""
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page_accessible_by_anonymous_user(client, news_item):
    """Страница новости доступна анонимному пользователю."""
    url = reverse('news:detail', kwargs={'pk': news_item.pk})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_deletion_requires_login(client, comment):
    """Анонимный пользователь не может удалить комментарий."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = client.post(url)
    login_url = reverse('users:login')
    expected_redirect_url = f"{login_url}?next={url}"
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url


@pytest.mark.django_db
def test_comment_deletion_accessible_to_author(authorized_client, comment):
    """Удаление комментария доступно автору."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = authorized_client.post(url)
    assert response.status_code == HTTPStatus.FOUND, "Автор должен иметь возможность удалить свой комментарий"
    comment_exists = Comment.objects.filter(pk=comment.pk).exists()
    assert not comment_exists, "Комментарий должен быть удалён"


@pytest.mark.django_db
def test_comment_deletion_inaccessible_to_other_users(another_authorized_client, comment):
    """Удаление комментария недоступно другим пользователям."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = another_authorized_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, "Другой пользователь не должен иметь доступа к удалению комментария"
    comment_exists = Comment.objects.filter(pk=comment.pk).exists()
    assert comment_exists, "Комментарий не должен быть удалён другим пользователем"


@pytest.mark.django_db
def test_authenticated_user_can_access_comment_form(authorized_client, news_item):
    """Авторизованный пользователь может получить доступ к форме комментариев на странице новости."""
    url = reverse('news:detail', kwargs={'pk': news_item.pk})
    response = authorized_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context, "Форма комментариев должна быть в контексте"


@pytest.mark.django_db
def test_anonymous_user_cannot_access_comment_form(client, news_item):
    """Анонимный пользователь не видит форму для добавления комментария на странице новости."""
    url = reverse('news:detail', kwargs={'pk': news_item.pk})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context, "Анонимный пользователь не должен видеть форму комментариев"
