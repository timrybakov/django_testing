import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        detail_news_url, form_data_1, client
):
    base_comments_count = Comment.objects.count()
    client.post(detail_news_url, data=form_data_1)
    comments_count = Comment.objects.count()
    assert comments_count == base_comments_count


@pytest.mark.django_db
def test_user_can_create_comment(
        detail_news_url,
        form_data_1,
        admin_client,
        admin_user,
        news
):
    response = admin_client.post(detail_news_url, data=form_data_1)
    assertRedirects(response, f'{detail_news_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data_1['text']
    assert comment.news == news
    assert comment.author == admin_user


@pytest.mark.django_db
def test_user_cant_use_bad_words(
        detail_news_url, admin_client, form_data_2
):
    response = admin_client.post(
        detail_news_url,
        data=form_data_2
    )
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(
        detail_news_url, delete_comment_url, author_client, news
):
    url_to_comments = detail_news_url + '#comments'
    response = author_client.delete(delete_comment_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    delete_comment_url, admin_client, news
):
    response = admin_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
        comment,
        author_client,
        edit_comment_url,
        form_data_3,
        detail_news_url
):
    url_to_comments = detail_news_url + '#comments'
    response = author_client.post(
        edit_comment_url,
        data=form_data_3
    )
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data_3['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        comment,
        admin_client,
        form_data_3,
        edit_comment_url
):
    response = admin_client.post(
        edit_comment_url,
        data=form_data_3
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    new_text = Comment.objects.get()
    assert comment.text == new_text.text
