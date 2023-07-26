from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            slug='slug',
            author=cls.author
        )

    def test_context(self):
        url = reverse('notes:list')
        user_notes_count = (
            (self.author_client, 1),
            (self.reader_client, 0)
        )
        for user_client, expected_count in user_notes_count:
            response = user_client.get(url)
            object_list = response.context['object_list']
            count = len(object_list)
            with self.subTest():
                self.assertEqual(
                    count,
                    expected_count
                )

    def test_form_in_add_create(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.author_client.get(url)
            with self.subTest(name=name):
                self.assertIn(
                    'form',
                    response.context
                )
