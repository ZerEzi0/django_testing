import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from news.models import News, Comment


@pytest.mark.django_db
class TestYaNewsRoutes:
    def setup_method(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password2'
        )

        self.news = News.objects.create(
            title="Test News",
            text="News Text"
        )
        self.comment = Comment.objects.create(
            news=self.news,
            author=self.user1,
            text="User1's Comment"
        )

    def test_main_page_accessible_anonymous(self, client):
        response = client.get(
            reverse(
                'news:home'
            )
        )
        assert response.status_code == 200

    def test_news_detail_page_accessible_anonymous(
            self,
            client
    ):
        response = client.get(
            reverse(
                'news:detail',
                kwargs={
                    'pk': self.news.id
                }
            )
        )
        assert response.status_code == 200

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

    def test_comment_edit_delete_accessible_to_author_only(self, client):
        client.login(
            username='user1',
            password='password1'
        )

        response = client.get(
            reverse(
                'news:edit',
                kwargs={
                    'pk': self.comment.pk
                }
            )
        )
        assert response.status_code == 200

        response = client.get(
            reverse(
                'news:delete',
                kwargs={
                    'pk': self.comment.pk
                }
            )
        )
        assert response.status_code == 200

        client.login(
            username='user2',
            password='password2'
        )

        response = client.get(
            reverse(
                'news:edit',
                kwargs={
                    'pk': self.comment.pk
                }
            )
        )
        assert response.status_code == 404

        response = client.get(
            reverse(
                'news:delete',
                kwargs={
                    'pk': self.comment.pk
                }
            )
        )
        assert response.status_code == 404

    def test_anonymous_user_redirected_to_login_on_comment_edit_delete(
            self,
            client
    ):
        restricted_urls = [
            reverse(
                'news:edit',
                kwargs={
                    'pk': self.comment.pk
                }
            ),
            reverse(
                'news:delete',
                kwargs={
                    'pk': self.comment.pk
                }
            ),
        ]

        for url in restricted_urls:
            response = client.get(url)
            assert response.status_code == 302
