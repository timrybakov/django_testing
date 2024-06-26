import pytest

from django.conf import settings


@pytest.mark.django_db
def test_count_newses_on_page(
        newses, client, home_url
):
    response = client.get(home_url)
    object_list = response.context['object_list']
    object_list_count = len(object_list)
    assert object_list_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_date_sorting(
        newses, client, home_url
):
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(
        news, client, comments, detail_news_url
):
    response = client.get(detail_news_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates_comments = [comment.created for comment in all_comments]
    sorted_list_comments = sorted(all_dates_comments)
    assert all_dates_comments == sorted_list_comments


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_result',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True)
    )
)
def test_anonymous_client_has_no_form(
        detail_news_url, parametrized_client, expected_result
):
    response = parametrized_client.get(detail_news_url)
    assert ('form' in response.context) == expected_result
