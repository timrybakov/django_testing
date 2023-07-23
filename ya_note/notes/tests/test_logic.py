from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from http import HTTPStatus

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):

    MESSAGE: str = 'Щука'
    SLUGIFY_MESSAGE: str = 'schuka'
    BASE_NOTES_COUNT: int = 1

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.redirect_url = reverse('notes:success')
        cls.note = Note.objects.create(
            text='Text',
            slug='slug',
            author=cls.user
        )
        cls.form_data_1 = {
            'title': 'Title',
            'text': 'Text',
            'slug': 'slugify'
        }
        cls.form_data_2 = {
            'title': f'{cls.MESSAGE}',
            'text': 'Text'
        }
        cls.form_data_3 = {
            'title': 'Title',
            'text': 'Text',
            'slug': 'slug'
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(
            self.url,
            data=self.form_data_1
        )
        total_count = Note.objects.count()
        self.assertEqual(
            total_count,
            self.BASE_NOTES_COUNT
        )

    def test_user_can_create_note(self):
        response = self.auth_client.post(
            self.url,
            data=self.form_data_1
        )
        self.assertRedirects(
            response,
            self.redirect_url
        )
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            self.BASE_NOTES_COUNT + 1
        )

    def test_user_cant_send_same_slug(self):
        response = self.auth_client.post(self.url, data=self.form_data_3)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.note.slug + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            self.BASE_NOTES_COUNT
        )

    def test_translit_slugify_title(self):
        self.auth_client.post(
            self.url,
            data=self.form_data_2
        )
        note = Note.objects.last()
        self.assertEqual(
            note.slug,
            self.SLUGIFY_MESSAGE
        )
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            self.BASE_NOTES_COUNT + 1
        )


class TestNoteUpdateDelete(TestCase):

    BASE_NOTES_COUNT: int = 1
    NEW_NOTE_TEXT: str = 'NEW_TEXT'
    BASE_NOTE_TEXT: str = 'Text'

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

        cls.note_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')

        cls.form_data = {
            'title': cls.note.title,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(
            response,
            self.redirect_url
        )
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            self.BASE_NOTES_COUNT - 1
        )

    def test_reader_cant_delete_note(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            self.BASE_NOTES_COUNT
        )

    def test_author_can_edit_note(self):
        self.author_client.post(
            self.note_edit_url,
            data=self.form_data
        )
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.text,
            self.NEW_NOTE_TEXT
        )

    def test_reader_cant_edit_note(self):
        response = self.reader_client.post(
            self.note_edit_url,
            data=self.form_data
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )
        self.note.refresh_from_db()
        self.assertEqual(
            self.note.text,
            self.BASE_NOTE_TEXT
        )
