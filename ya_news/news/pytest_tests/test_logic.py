import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        news, form_data_1, client
):
    url = reverse('news:detail', args=(news.pk,))
    client.post(url, data=form_data_1)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(
        news, form_data_1, admin_client, admin_user
):
    url = reverse('news:detail', args=(news.pk,))
    response = admin_client.post(url, data=form_data_1)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == 'Comment text'
    assert comment.news == news
    assert comment.author == admin_user


@pytest.mark.django_db
def test_user_cant_use_bad_words(
        news, admin_client, form_data_2
):
    url = reverse('news:detail', args=(news.pk,))
    response = admin_client.post(url, data=form_data_2)
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
        comment, author_client, news
):
    url = reverse('news:delete', args=(comment.pk,))
    url_to_comments = reverse('news:detail', args=(news.pk,)) + '#comments'
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    comment, admin_client, news
):
    url = reverse('news:delete', args=(comment.pk,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
        comment, author_client, news, form_data_3
):
    url = reverse('news:edit', args=(comment.pk,))
    url_to_comments = reverse('news:detail', args=(news.pk,)) + '#comments'
    response = author_client.post(url, data=form_data_3)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == 'New text'


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    comment, admin_client, news, form_data_3
):
    url = reverse('news:edit', args=(comment.pk,))
    response = admin_client.post(url, data=form_data_3)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Text'
