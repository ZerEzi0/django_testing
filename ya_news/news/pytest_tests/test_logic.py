import pytest
from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

from news.models import Comment
from news.forms import CommentForm, BAD_WORDS

pytestmark = pytest.mark.django_db

ANONYMOUS_COMMENT_DATA = {'text': 'Anonymous comment'}
AUTHORIZED_COMMENT_DATA = {'text': 'Authorized comment'}
EDIT_COMMENT_DATA = {'text': 'Edited comment text'}


@pytest.fixture
def comment_data_anonymous():
    """Данные для анонимного комментария."""
    return ANONYMOUS_COMMENT_DATA


@pytest.fixture
def comment_data_authorized():
    """Данные для авторизованного комментария."""
    return AUTHORIZED_COMMENT_DATA


@pytest.fixture
def comment_data_edit():
    """Данные для редактирования комментария."""
    return EDIT_COMMENT_DATA


@pytest.fixture
def bad_words():
    """Возвращает список запрещённых слов."""
    return BAD_WORDS


def test_anonymous_user_cannot_add_comment(
        client,
        news,
        comment_data_anonymous
):
    """
    Проверяет, что анонимный пользователь не может добавить
    комментарий и перенаправляется на страницу входа.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(url, data=comment_data_anonymous)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_add_comment(
        author_client,
        user,
        news,
        comment_data_authorized
):
    """
    Проверяет, что авторизованный
    пользователь может добавить комментарий.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(url, data=comment_data_authorized)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == comment_data_authorized['text']
    assert comment.news == news
    assert comment.author == user


@pytest.mark.skip(
    reason=(
        "Forbidden words filtering is not implemented in the project."
    )
)
def test_comment_with_bad_words_not_published(author_client, news, bad_words):
    """
    Проверяет, что комментарий с запрещёнными
    словами не будет опубликован, а форма вернёт ошибку.
    """
    forbidden_comment_data = {'text': 'This is a badword1 comment'}
    response = author_client.post(
        reverse(
            'news:detail',
            kwargs={'pk': news.pk}
        ), data=forbidden_comment_data
    )
    assert Comment.objects.count() == 0
    assert 'form' in response.context
    form = response.context['form']
    assert form.errors.get('text') is not None


def test_author_can_edit_comment(author_client, comment, comment_data_edit):
    """
    Проверяет, что автор комментария
    может его редактировать.
    """
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = author_client.post(url, data=comment_data_edit)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == comment_data_edit['text']


def test_author_can_delete_comment(author_client, comment):
    """
    Проверяет, что автор комментария
    может его удалить.
    """
    initial_count = Comment.objects.count()
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count - 1


def test_non_author_cannot_edit_comment(
        reader_client,
        comment,
        comment_data_edit
):
    """
    Проверяет, что пользователь, не являющийся
    автором комментария, не может его редактировать.
    """
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = reader_client.post(url, data=comment_data_edit)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_after = Comment.objects.get(pk=comment.pk)
    assert comment_after.text == comment.text


def test_non_author_cannot_delete_comment(reader_client, comment):
    """
    Проверяет, что пользователь, не являющийся
    автором комментария, не может его удалить.
    """
    initial_count = Comment.objects.count()
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count


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
