import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from news.models import News, Comment
from news.forms import BAD_WORDS

@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')

@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client

@pytest.fixture
def news():
    return News.objects.create(
        title='Title',
        text='Text'
    )

@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Text'
    )

@pytest.fixture
def newses():
    today = datetime.today()
    return News.objects.bulk_create(
            News(
                title=f'News {index}',
                text='Text',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )

@pytest.fixture
def comments(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Text {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comment

@pytest.fixture
def form_data_1():
    return {'text': 'Comment text'}

@pytest.fixture
def form_data_2():
    return {'text': f'Comment text {BAD_WORDS[0]}'}

@pytest.fixture
def form_data_3():
    return {'text': 'New text'}
