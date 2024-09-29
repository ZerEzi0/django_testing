import pytest
from django.urls import reverse
from http import HTTPStatus

pytestmark = pytest.mark.django_db


def test_home_page_available_to_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_news_detail_available_to_anonymous_user(client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_comment_edit_delete_pages_available_to_author(
    auth_client,
    comment, url_name
):
    url = reverse(url_name, kwargs={'pk': comment.pk})
    response = auth_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_comment_edit_delete_redirects_for_anonymous_user(
    client,
    comment,
    url_name
):
    url = reverse(url_name, kwargs={'pk': comment.pk})
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


@pytest.mark.parametrize('url_name', ['news:edit', 'news:delete'])
def test_comment_edit_delete_404_for_non_author(
    another_auth_client,
    comment,
    url_name
):
    url = reverse(url_name, kwargs={'pk': comment.pk})
    response = another_auth_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_name',
    [
        'users:signup',
        'users:login',
        'users:logout'
    ]
)
def test_auth_pages_available_to_anonymous_users(
    client,
    url_name
):
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
