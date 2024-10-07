from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_home_url'),
    pytest.lazy_fixture('news_detail_url'),
])
def test_pages_accessible_to_anonymous_user(client, url):
    """Проверяет доступность страниц для анонимного пользователя."""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_edit_url'),
    pytest.lazy_fixture('news_delete_url'),
])
def test_author_access_to_comment_edit_delete(author_client, url):
    """
    Проверяет, что автор комментария может
    получить доступ к страницам редактирования и удаления.
    """
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_edit_url'),
    pytest.lazy_fixture('news_delete_url'),
])
def test_redirect_anonymous_user_from_comment_edit_delete(
    client,
    url,
    users_login_url
):
    """Проверяет перенаправление анонимного пользователя
    при попытке редактировать или удалить комментарий.
    """
    response = client.get(url)
    expected_url = f'{users_login_url}?next={url}'
    assertRedirects(response, expected_url)


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('news_edit_url'),
    pytest.lazy_fixture('news_delete_url'),
])
def test_non_author_access_denied_to_comment_edit_delete(reader_client, url):
    """Проверяет, что не автор комментария не может
    получить доступ к страницам редактирования и удаления.
    """
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('url', [
    pytest.lazy_fixture('users_signup_url'),
    pytest.lazy_fixture('users_login_url'),
    pytest.lazy_fixture('users_logout_url'),
])
def test_auth_pages_available_to_anonymous_users(client, url):
    """
    Проверяет доступность страниц аутентификации
    для анонимных пользователей.
    """
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
