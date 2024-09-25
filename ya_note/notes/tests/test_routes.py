import pytest
from django.urls import reverse
from http import HTTPStatus
from django.conf import settings


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', [
    'notes:home',
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
def test_notes_list_redirects_anonymous_user_to_login(client):
    """Анонимный пользователь перенаправляется на страницу логина при попытке доступа к списку заметок."""
    url = reverse('notes:list')
    login_url = str(settings.LOGIN_URL)
    expected_redirect_url = f"{login_url}?next={url}"
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['notes:add', 'notes:success'])
def test_anonymous_user_redirected_to_login_on_restricted_pages(client, url_name):
    """Анонимный пользователь перенаправляется на страницу логина при попытке доступа к закрытым страницам."""
    url = reverse(url_name)
    login_url = str(settings.LOGIN_URL)
    expected_redirect_url = f"{login_url}?next={url}"
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url


@pytest.mark.django_db
def test_anonymous_user_redirected_to_login_on_note_detail(client, note):
    """Анонимный пользователь перенаправляется на страницу логина при попытке доступа к деталям заметки."""
    url = reverse('notes:detail', kwargs={'slug': note.slug})
    login_url = str(settings.LOGIN_URL)
    expected_redirect_url = f"{login_url}?next={url}"
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url


@pytest.mark.django_db
@pytest.mark.parametrize('client_fixture, expected_status', [
    ('author_client', HTTPStatus.OK),
    ('another_user_client', HTTPStatus.NOT_FOUND),
])
def test_note_detail_accessible_only_to_author(
    request,
    note,
    client_fixture,
    expected_status
):
    """Страница заметки доступна только автору, остальные получают 404."""
    client = request.getfixturevalue(client_fixture)
    url = reverse('notes:detail', kwargs={'slug': note.slug})
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('client_fixture, expected_status', [
    ('author_client', HTTPStatus.OK),
    ('another_user_client', HTTPStatus.NOT_FOUND),
])
@pytest.mark.parametrize('url_name', ['notes:edit', 'notes:delete'])
def test_note_edit_delete_accessible_only_to_author(
    request,
    note,
    client_fixture,
    expected_status,
    url_name
):
    """Страницы редактирования и удаления заметки доступны только автору."""
    client = request.getfixturevalue(client_fixture)
    url = reverse(url_name, kwargs={'slug': note.slug})
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
def test_authorized_user_can_access_notes_pages(author_client):
    """Авторизованный пользователь может получить доступ к страницам заметок."""
    urls = [
        reverse('notes:list'),
        reverse('notes:add'),
        reverse('notes:success'),
    ]
    for url in urls:
        response = author_client.get(url)
        assert response.status_code == HTTPStatus.OK
