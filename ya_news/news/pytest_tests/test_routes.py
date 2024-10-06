import pytest
from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('url_name', ['news:home', 'news:detail'])
def test_pages_accessible_to_anonymous_user(client, news, url_name):
    """Проверяет доступность страниц для анонимного пользователя."""
    if url_name == 'news:detail':
        url = reverse(url_name, kwargs={'pk': news.pk})
    else:
        url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_author_access_to_comment_edit_delete(
    author_client,
    comment,
    url_name
):
    """Проверяет, что автор комментария может
    получить доступ к страницам редактирования и удаления.
    """
    url = reverse(url_name, kwargs={'pk': comment.pk})
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_redirect_anonymous_user_from_comment_edit_delete(
    client,
    comment,
    url_name
):
    """Проверяет перенаправление анонимного пользователя
    при попытке редактировать или удалить комментарий.
    """
    url = reverse(url_name, kwargs={'pk': comment.pk})
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_non_author_access_denied_to_comment_edit_delete(
    reader_client,
    comment,
    url_name
):
    """Проверяет, что не автор комментария не может
    получить доступ к страницам редактирования и удаления.
    """
    url = reverse(url_name, kwargs={'pk': comment.pk})
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_name',
    [
        'users:signup',
        'users:login',
        'users:logout'
    ]
)
def test_auth_pages_available_to_anonymous_users(client, url_name):
    """
    Проверяет доступность страниц аутентификации
    для анонимных пользователей.
    """
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
