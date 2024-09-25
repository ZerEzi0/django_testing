import pytest
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


@pytest.mark.django_db
def test_note_in_object_list(author_client, another_user_client, note):
    """Проверяет, что автор видит свою заметку в списке, а другой пользователь — нет."""
    clients_expected = [
        (author_client, True),
        (another_user_client, False),
    ]
    url = reverse('notes:list')
    for client, expected in clients_expected:
        response = client.get(url)
        object_list = response.context.get('object_list', [])
        note_in_list = note in object_list
        assert note_in_list == expected, (
            f"Заметка должна {
                'присутствовать' if expected else 'отсутствовать'
            } в списке для данного пользователя."
        )


@pytest.mark.django_db
def test_note_form_in_creation_and_edit_pages(author_client, note):
    """Проверяет, что на страницах создания и редактирования заметки передаётся форма NoteForm."""
    urls = [
        ('notes:add', {}),
        ('notes:edit', {'slug': note.slug}),
    ]
    for url_name, kwargs in urls:
        url = reverse(url_name, kwargs=kwargs)
        response = author_client.get(url)
        assert 'form' in response.context, "В контексте ответа отсутствует форма 'form'."
        form = response.context['form']
        assert isinstance(form, NoteForm), "Форма в контексте не является экземпляром NoteForm."
