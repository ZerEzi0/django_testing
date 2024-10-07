from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db

COMMENT_DATA = {'text': 'Test comment'}


def test_anonymous_user_cannot_add_comment(
    client,
    news_detail_url,
    users_login_url
):
    """Проверяет, что анонимный пользователь не может добавить комментарий."""
    response = client.post(news_detail_url, data=COMMENT_DATA)
    expected_url = f'{users_login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_add_comment(author_client, user, news_detail_url):
    """
    Проверяет, что авторизованный пользователь
    может добавить комментарий.
    """
    response = author_client.post(
        news_detail_url,
        data=COMMENT_DATA
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_DATA['text']
    news_id = int(news_detail_url.strip('/').split('/')[-1])
    assert comment.news.pk == news_id
    assert comment.author == user


def test_comment_with_bad_words_not_published(author_client, news_detail_url):
    """
    Проверяет, что комментарий
    с запрещёнными словами не будет опубликован.
    """
    forbidden_comment_text = f'This is a {BAD_WORDS[0]} comment'
    response = author_client.post(
        news_detail_url,
        data={'text': forbidden_comment_text}
    )
    assert Comment.objects.count() == 0
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


def test_author_can_edit_comment(author_client, comment):
    """Проверяет, что автор комментария может его редактировать."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    new_comment_data = {'text': 'Edited comment text'}
    response = author_client.post(url, data=new_comment_data)
    assert response.status_code == HTTPStatus.FOUND
    comment_after = Comment.objects.get(pk=comment.pk)
    assert comment_after.text == new_comment_data['text']


def test_author_can_delete_comment(author_client, comment):
    """Проверяет, что автор комментария может его удалить."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_non_author_cannot_edit_comment(reader_client, comment):
    """Проверяет, что не автор комментария не может его редактировать."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    original_text = comment.text
    new_comment_data = {'text': 'Edited by non-author'}
    response = reader_client.post(url, data=new_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_after = Comment.objects.get(pk=comment.pk)
    assert comment_after.text == original_text


def test_non_author_cannot_delete_comment(reader_client, comment):
    """Проверяет, что не автор комментария не может его удалить."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
