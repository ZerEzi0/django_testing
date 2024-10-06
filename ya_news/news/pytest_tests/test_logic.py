from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.models import Comment
from news.forms import BAD_WORDS

pytestmark = pytest.mark.django_db

ANONYMOUS_COMMENT_TEXT = 'Anonymous comment'
AUTHORIZED_COMMENT_TEXT = 'Authorized comment'
EDITED_COMMENT_TEXT = 'Edited comment text'


def test_anonymous_user_cannot_add_comment(client, news):
    """Проверяет, что анонимный пользователь не может добавить комментарий."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(url, data={'text': ANONYMOUS_COMMENT_TEXT})
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_add_comment(author_client, user, news):
    """
    Проверяет, что авторизованный пользователь
    может добавить комментарий.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(
        url,
        data={'text': AUTHORIZED_COMMENT_TEXT}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == AUTHORIZED_COMMENT_TEXT
    assert comment.news == news
    assert comment.author == user


def test_comment_with_bad_words_not_published(author_client, news):
    """
    Проверяет, что комментарий
    с запрещёнными словами не будет опубликован.
    """
    forbidden_comment_text = f'This is a {BAD_WORDS[0]} comment'
    response = author_client.post(
        reverse('news:detail', kwargs={'pk': news.pk}),
        data={'text': forbidden_comment_text}
    )
    assert Comment.objects.count() == 0
    assert 'form' in response.context, 'В контексте отсутствует форма'
    form = response.context['form']
    assert form.errors.get('text') is not None, (
        'Форма не содержит ошибок в поле text'
    )


def test_author_can_edit_comment(author_client, comment):
    """Проверяет, что автор комментария может его редактировать."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = author_client.post(url, data={'text': EDITED_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == EDITED_COMMENT_TEXT


def test_author_can_delete_comment(author_client, comment):
    """Проверяет, что автор комментария может его удалить."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_non_author_cannot_edit_comment(reader_client, comment):
    """Проверяет, что не автор комментария не может его редактировать."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = reader_client.post(url, data={'text': EDITED_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != EDITED_COMMENT_TEXT


def test_non_author_cannot_delete_comment(reader_client, comment):
    """Проверяет, что не автор комментария не может его удалить."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
