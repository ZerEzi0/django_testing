import pytest
from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


def test_anonymous_user_pages_access(client, news):
    """
    Проверяет доступность всех
    страниц для анонимного пользователя.
    """
    urls = [
        reverse('news:home'),
        reverse('news:detail', kwargs={'pk': news.pk}),
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_comment_edit_delete_pages_available_to_author(
    author_client,
    comment,
    url_name
):
    """
    Проверяет, что автор комментария может
    получить доступ к страницам редактирования и удаления.
    """
    url = reverse(url_name, kwargs={'pk': comment.pk})
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_comment_edit_delete_redirects_for_anonymous_user(
    client,
    comment,
    url_name
):
    """
    Проверяет, что анонимный пользователь перенаправляется на страницу входа
    при попытке редактировать или удалить комментарий.
    """
    url = reverse(url_name, kwargs={'pk': comment.pk})
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_comment_edit_delete_404_for_non_author(
    reader_client,
    comment,
    url_name
):
    """
    Проверяет, что пользователь, не являющийся автором комментария,
    получает ошибку 404 при попытке редактировать или удалить комментарий.
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
    Проверяет доступность страниц
    аутентификации для анонимных пользователей.
    """
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
