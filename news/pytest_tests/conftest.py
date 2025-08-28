from datetime import timedelta

from django.conf import settings
from django.test.client import Client
from django.utils import timezone
import pytest

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=timezone.now()
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comment_form_data():
    return {'text': 'Новый текст'}


@pytest.fixture
def pk_for_args(news):
    return (news.pk,)


@pytest.fixture
def comment_pk_for_args(comment):
    return (comment.pk,)


@pytest.fixture
def news_column():
    today = timezone.now()
    news_column = [
        News(
            title='Заголовок',
            text='Текст новости',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(news_column)


@pytest.fixture
def comments(author, news):
    today = timezone.now()
    for index in range(1):
        comments = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comments.created = today + timedelta(days=index)
        comments.save()
    return comments
