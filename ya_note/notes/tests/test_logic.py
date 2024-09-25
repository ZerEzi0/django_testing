import pytest
from django.urls import reverse
from pytils.translit import slugify
from http import HTTPStatus

from notes.models import Note


@pytest.mark.django_db
def test_authenticated_user_can_create_note(author_client, note_form_data):
    """Авторизованный пользователь может создать заметку."""
    url = reverse('notes:add')
    notes_count_before = Note.objects.count()
    response = author_client.post(url, data=note_form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Note.objects.count() == notes_count_before + 1
    new_note = Note.objects.latest('id')
    for field in note_form_data:
        assert getattr(new_note, field) == note_form_data[field], (
            f"Поле {field} не совпадает"
        )


@pytest.mark.django_db
def test_anonymous_user_cannot_create_note(client, note_form_data):
    """Анонимный пользователь не может создать заметку."""
    url = reverse('notes:add')
    response = client.post(url, data=note_form_data)
    login_url = str(reverse('users:login'))
    expected_redirect_url = f"{login_url}?next={url}"
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url
    assert not Note.objects.filter(
        title=note_form_data['title']
    ).exists(), "Заметка не должна быть создана анонимным пользователем"


@pytest.mark.django_db
def test_slug_is_generated_if_not_provided(
    author_client,
    note_form_data_without_slug
):
    """Если slug не указан, он генерируется автоматически."""
    url = reverse('notes:add')
    response = author_client.post(url, data=note_form_data_without_slug)
    assert response.status_code == HTTPStatus.FOUND
    note = Note.objects.get(title=note_form_data_without_slug['title'])
    expected_slug = slugify(note_form_data_without_slug['title'])
    assert note.slug == expected_slug, "Slug не сгенерирован автоматически"


@pytest.mark.django_db
def test_cannot_create_note_with_duplicate_slug(
    author_client,
    note,
    note_form_data
):
    """Невозможно создать две заметки с одинаковым slug."""
    note_form_data['slug'] = note.slug
    url = reverse('notes:add')
    notes_count_before = Note.objects.count()
    response = author_client.post(url, data=note_form_data)
    assert response.status_code == HTTPStatus.OK
    form = response.context.get('form')
    assert form is not None, "Форма отсутствует в контексте"
    assert 'slug' in form.errors, "Ошибки отсутствуют в поле 'slug'"
    assert Note.objects.count() == notes_count_before, (
        "Количество заметок не должно увеличиться при ошибке"
    )


@pytest.mark.django_db
def test_user_can_edit_own_note(author_client, note):
    """Пользователь может редактировать свою заметку."""
    url = reverse('notes:edit', kwargs={'slug': note.slug})
    form_data = {
        'title': 'Edited Note',
        'text': 'Edited Text',
        'slug': note.slug,
    }
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    note.refresh_from_db()
    for field in form_data:
        assert getattr(note, field) == form_data[field], (
            f"Поле {field} не обновлено"
        )


@pytest.mark.django_db
def test_user_cannot_edit_another_user_note(another_user_client, note):
    """Пользователь не может редактировать чужую заметку."""
    url = reverse('notes:edit', kwargs={'slug': note.slug})
    form_data = {
        'title': 'Edited by Another User',
        'text': 'Edited Text',
        'slug': note.slug,
    }
    notes_count_before = Note.objects.count()
    response = another_user_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note.refresh_from_db()
    assert note.title != form_data['title'], (
        "Заголовок заметки не должен быть изменён"
    )
    assert note.text != form_data['text'], (
        "Текст заметки не должен быть изменён"
    )
    assert Note.objects.count() == notes_count_before, (
        "Количество заметок не должно измениться"
    )


@pytest.mark.django_db
def test_user_can_delete_own_note(author_client, note):
    """Пользователь может удалить свою заметку."""
    url = reverse('notes:delete', kwargs={'slug': note.slug})
    notes_count_before = Note.objects.count()
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Note.objects.count() == notes_count_before - 1, (
        "Количество заметок должно уменьшиться на 1"
    )
    assert not Note.objects.filter(slug=note.slug).exists(), (
        "Заметка должна быть удалена"
    )


@pytest.mark.django_db
def test_user_cannot_delete_another_user_note(
    another_user_client,
    note
):
    """Пользователь не может удалить чужую заметку."""
    url = reverse('notes:delete', kwargs={'slug': note.slug})
    notes_count_before = Note.objects.count()
    response = another_user_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == notes_count_before, (
        "Количество заметок не должно измениться"
    )
    assert Note.objects.filter(slug=note.slug).exists(), (
        "Заметка не должна быть удалена другим пользователем"
    )
