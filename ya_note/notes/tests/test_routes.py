from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from http import HTTPStatus

from notes.models import Note

User = get_user_model()

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            slug='slug',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup'
        )
        for name in urls:
            url = reverse(name)
            response = self.client.get(url)
            with self.subTest(name=name):
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_pages_availability_list_add_done(self):
        urls = (
            'notes:add',
            'notes:list',
            'notes:success'
        )
        self.client.force_login(self.author)
        for name in urls:
            url = reverse(name)
            response = self.client.get(url)
            with self.subTest(name=name):
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_pages_availability_detail_edit_delete(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete'
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in urls:
                url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                with self.subTest(name=name):
                    self.assertEqual(
                        response.status_code,
                        status
                    )

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            url = reverse(name, args=args)
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            with self.subTest(name=name, args=args):
                self.assertRedirects(
                    response,
                    redirect_url
                )
