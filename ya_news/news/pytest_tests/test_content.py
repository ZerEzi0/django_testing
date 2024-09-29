import pytest
from django.urls import reverse
from news.models import News, Comment

pytestmark = pytest.mark.django_db


def test_news_count_on_homepage(client):
    NUM_NEWS = 15
    news_list = [News(
        title=f'News {i}',
        text='Some text'
    ) for i in range(NUM_NEWS)]
    News.objects.bulk_create(news_list)
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context.get(
        'object_list'
    ) or response.context.get('news_list')
    expected_count = min(NUM_NEWS, 10)
    assert len(object_list) == expected_count


def test_news_order_on_homepage(client):
    news_old = News.objects.create(
        title='Old News',
        text='Some text'
    )
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context.get(
        'object_list'
    ) or response.context.get('news_list')

    news_titles = [news.title for news in object_list]
    print("News titles on homepage:", news_titles)
    assert list(object_list)[0] == news_old


def test_comments_order_on_news_detail(client, news, user):
    comment_old = Comment.objects.create(
        news=news,
        author=user,
        text='First comment'
    )
    comment_new = Comment.objects.create(
        news=news,
        author=user,
        text='Second comment'
    )
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    news_in_context = response.context.get(
        'news'
    ) or response.context.get('object')
    comments_in_context = getattr(news_in_context, 'comments', None)
    if comments_in_context is None:
        comments_in_context = news_in_context.comment_set.all()
    else:
        comments_in_context = news_in_context.comments.all()

    comments_texts = [
        comment.text for comment in comments_in_context
    ]
    print("Comments texts on news detail page:", comments_texts)

    assert list(comments_in_context)[0] == comment_old
    assert list(comments_in_context)[1] == comment_new


@pytest.mark.parametrize('client_fixture, form_expected', [
    ('client', False),
    ('auth_client', True),
])
def test_comment_form_visibility(
    client_fixture,
    form_expected,
    request,
    news
):
    client = request.getfixturevalue(client_fixture)
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert ('form' in response.context) == form_expected
