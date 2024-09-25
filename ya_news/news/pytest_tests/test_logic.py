import pytest
from django.urls import reverse
from http import HTTPStatus

from news.models import Comment


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(
    authorized_client,
    news_item,
    user
):
    """Авторизованный пользователь может оставить комментарий."""
    url = reverse('news:detail', kwargs={'pk': news_item.pk})
    data = {'text': 'Новый комментарий'}
    response = authorized_client.post(url, data=data)
    assert response.status_code == HTTPStatus.FOUND, (
        "Ожидается перенаправление после успешного поста"
    )
    comment_exists = Comment.objects.filter(
        news=news_item,
        author=user,
        text='Новый комментарий'
    ).exists()
    assert comment_exists, "Комментарий не был создан"


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client, news_item):
    """Анонимный пользователь не может оставить комментарий."""
    url = reverse('news:detail', kwargs={'pk': news_item.pk})
    data = {'text': 'Комментарий от анонимного пользователя'}
    response = client.post(url, data=data)
    login_url = reverse('users:login')
    expected_redirect_url = f"{login_url}?next={url}"
    assert response.status_code == HTTPStatus.FOUND, (
        "Ожидается перенаправление на страницу логина"
    )
    assert response.url == expected_redirect_url, (
        "Анонимный пользователь должен быть перенаправлен на страницу логина"
    )
    comment_exists = Comment.objects.filter(
        news=news_item,
        text='Комментарий от анонимного пользователя'
    ).exists()
    assert not comment_exists, (
        "Комментарий не должен быть создан анонимным пользователем"
    )


@pytest.mark.django_db
def test_comment_with_forbidden_words_not_published(
    authorized_client,
    news_item,
    user
):
    """Комментарий с запрещёнными словами не публикуется."""
    url = reverse('news:detail', kwargs={'pk': news_item.pk})
    forbidden_word = 'редиска'
    data = {'text': f'Это {forbidden_word} комментарий'}
    response = authorized_client.post(url, data=data)
    assert response.status_code == HTTPStatus.OK, (
        f"Ожидался статус код 200, но получен {response.status_code}"
    )
    comment_exists = Comment.objects.filter(
        news=news_item,
        author=user,
        text__icontains=forbidden_word
    ).exists()
    assert not comment_exists, (
        "Комментарий с запрещёнными словами не должен публиковаться"
    )
    assert 'form' in response.context, "Форма отсутствует в контексте"
    form = response.context['form']
    assert form.errors, "Ожидались ошибки в форме"
    assert 'text' in form.errors, "Ошибка должна быть в поле 'text'"


@pytest.mark.django_db
def test_user_can_delete_own_comment(
    authorized_client,
    comment
):
    url = reverse(
        'news:delete',
        kwargs={'pk': comment.pk}
    )
    comments_count_before = Comment.objects.count()
    response = authorized_client.post(url)
    assert response.status_code == HTTPStatus.FOUND, (
        "Ожидается перенаправление после удаления комментария"
    )
    assert Comment.objects.count() == comments_count_before - 1, (
        "Комментарий должен быть удалён"
    )


@pytest.mark.django_db
def test_user_cannot_delete_another_user_comment(
    authorized_client,
    comment_from_another_user
):
    """Пользователь не может удалить чужой комментарий."""
    url = reverse('news:delete', kwargs={'pk': comment_from_another_user.pk})
    comments_count_before = Comment.objects.count()
    response = authorized_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        "Ожидается статус код 404 при попытке удаления чужого комментария"
    )
    assert Comment.objects.count() == comments_count_before, (
        "Комментарий не должен быть удалён другим пользователем"
    )
