import pytest

from django.urls import reverse
from django.conf import settings


@pytest.mark.django_db
def test_count_newses_on_page(newses, client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    object_list_count = len(object_list)
    assert object_list_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_date_sorting(newses, client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(news, client, comments):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_result',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True)
    )
)
def test_anonymous_client_has_no_form(
        news, parametrized_client, expected_result
):
    url = reverse('news:detail', args=(news.pk,))
    response = parametrized_client.get(url)
    if 'form' in response.context:
        result = True
    else:
        result = False
    assert result == expected_result
