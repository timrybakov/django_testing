from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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

    def test_context(self):
        url = reverse('notes:list')
        user_notes_count = (
            (self.author, 1),
            (self.reader, 0)
        )
        for user, expected_count in user_notes_count:
            self.client.force_login(user)
            response = self.client.get(url)
            object_list = response.context['object_list']
            count = len(object_list)
            with self.subTest(user=user):
                self.assertEqual(
                    count,
                    expected_count
                )

    def test_form_in_add_create(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        self.client.force_login(self.author)
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.client.get(url)
            with self.subTest(name=name):
                self.assertIn(
                    'form',
                    response.context
                )
