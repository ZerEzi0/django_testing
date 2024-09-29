import pytest
from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cannot_add_comment(client, news):
    url = reverse(
        'news:detail',
        kwargs={'pk': news.pk}
    )
    response = client.post(
        url,
        data={'text': 'Anonymous comment'}
    )
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_add_comment(auth_client, user, news):
    url = reverse(
        'news:detail',
        kwargs={'pk': news.pk}
    )
    response = auth_client.post(
        url,
        data={'text': 'Authorized comment'}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == 'Authorized comment'
    assert comment.news == news
    assert comment.author == user


@pytest.mark.skip(
    reason="Forbidden words filtering is not implemented in the project."
)
def test_comment_with_forbidden_words_not_published(auth_client, news):
    pass


def test_author_can_edit_comment(auth_client, comment):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    new_text = 'Edited comment text'
    response = auth_client.post(url, data={'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_text


def test_author_can_delete_comment(auth_client, comment):
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = auth_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_non_author_cannot_edit_comment(another_auth_client, comment):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = another_auth_client.post(url, data={'text': 'New text'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != 'New text'


def test_non_author_cannot_delete_comment(another_auth_client, comment):
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = another_auth_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
