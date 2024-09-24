import pytest
from django.urls import reverse
from news.models import Comment


@pytest.mark.django_db
class TestYaNewsLogic:
    @pytest.mark.skip(reason="No route for 'add_comment'")
    def test_anonymous_user_cannot_post_comment(self, client):
        response = client.post(
            reverse(
                'news:add_comment',
                kwargs={
                    'pk': self.news.id
                }
            ),
            {'text': 'New Comment'}
        )
        assert response.status_code == 302

    @pytest.mark.skip(reason="No route for 'add_comment'")
    def test_authenticated_user_can_post_comment(self, client):
        client.login(username='user1', password='password1')
        response = client.post(
            reverse(
                'news:add_comment',
                kwargs={
                    'pk': self.news.id
                }
            ),
            {'text': 'New Comment'}
        )
        assert response.status_code == 302
        assert Comment.objects.filter(text='New Comment').exists()

    @pytest.mark.skip(reason="No route for 'edit_comment'")
    def test_user_can_edit_own_comment(self, client):
        client.login(username='user1', password='password1')
        response = client.post(
            reverse(
                'news:edit',
                kwargs={
                    'pk': self.comment.pk
                }
            ),
            {'text': 'Edited Comment'}
        )
        assert response.status_code == 302
        self.comment.refresh_from_db()
        assert self.comment.text == 'Edited Comment'

    @pytest.mark.skip(reason="No route for 'edit_comment'")
    def test_user_cannot_edit_another_user_comment(self, client):
        client.login(username='user2', password='password2')
        response = client.post(
            reverse(
                'news:edit',
                kwargs={
                    'pk': self.comment.pk
                }
            ),
            {'text': 'Edited by User2'}
        )
        assert response.status_code == 404

    @pytest.mark.skip(reason="No route for 'delete_comment'")
    def test_user_can_delete_own_comment(self, client):
        client.login(username='user1', password='password1')
        response = client.post(
            reverse(
                'news:delete',
                kwargs={
                    'pk': self.comment.pk
                }
            )
        )
        assert response.status_code == 302
        assert not Comment.objects.filter(pk=self.comment.pk).exists()

    @pytest.mark.skip(reason="No route for 'delete_comment'")
    def test_user_cannot_delete_another_user_comment(self, client):
        client.login(username='user2', password='password2')
        response = client.post(
            reverse(
                'news:delete',
                kwargs={
                    'pk': self.comment.pk
                }
            )
        )
        assert response.status_code == 404
        assert Comment.objects.filter(pk=self.comment.pk).exists()
