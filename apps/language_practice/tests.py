from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.language_practice.models import Language, Vocabulary, UserVocabulary


User = get_user_model()


class LanguageModelTests(TestCase):
    """Test cases for the Language model."""

    def setUp(self):
        self.language_data = {'name': 'English'}

    def test_create_language(self):
        language = Language.objects.create(**self.language_data)

        self.assertIsNotNone(language.id)
        self.assertEqual(language.name, self.language_data['name'])
        self.assertTrue(language.enable)

    def test_language_duplicate_raises_error(self):
        Language.objects.create(**self.language_data)

        with self.assertRaises(Exception):
            Language.objects.create(**self.language_data)

    def test_language_string_representation(self):
        language = Language.objects.create(**self.language_data)

        self.assertEqual(str(language), language.name)


class VocabularyModelTests(TestCase):
    """Test cases for the Vocabulary model."""

    def setUp(self):
        self.language = Language.objects.create(name='English')
        self.vocabulary_data = {
            'word_vocab': 'beautiful',
            'language': self.language,
            'enable': True,
        }

    def test_create_vocabulary(self):
        vocabulary = Vocabulary.objects.create(**self.vocabulary_data)

        self.assertIsNotNone(vocabulary.id)
        self.assertEqual(vocabulary.word_vocab, self.vocabulary_data['word_vocab'])
        self.assertEqual(vocabulary.language, self.language)

    def test_vocabulary_duplicate_in_same_language_raises_error(self):
        Vocabulary.objects.create(**self.vocabulary_data)

        with self.assertRaises(Exception):
            Vocabulary.objects.create(**self.vocabulary_data)

    def test_vocabulary_duplicate_across_languages_raises_error(self):
        spanish = Language.objects.create(name='Spanish')
        Vocabulary.objects.create(word_vocab='beautiful', language=spanish)

        with self.assertRaises(Exception):
            Vocabulary.objects.create(word_vocab='beautiful', language=spanish)

    def test_vocabulary_string_representation(self):
        vocabulary = Vocabulary.objects.create(**self.vocabulary_data)

        self.assertEqual(str(vocabulary), vocabulary.word_vocab)

    def test_vocabulary_enable_disable(self):
        vocabulary = Vocabulary.objects.create(**self.vocabulary_data)

        self.assertTrue(vocabulary.enable)

        vocabulary.enable = False
        vocabulary.save()

        self.assertFalse(vocabulary.enable)


class UserVocabularyModelTests(TestCase):
    """Test cases for the UserVocabulary model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.language = Language.objects.create(name='English')
        self.vocabulary = Vocabulary.objects.create(
            word_vocab='serendipity',
            language=self.language,
            enable=True
        )

    def test_create_user_vocabulary(self):
        user_vocabulary = UserVocabulary.objects.create(
            user=self.user,
            vocabulary=self.vocabulary,
        )

        self.assertIsNotNone(user_vocabulary.id)
        self.assertEqual(user_vocabulary.user, self.user)
        self.assertEqual(user_vocabulary.vocabulary, self.vocabulary)
        self.assertEqual(user_vocabulary.practice_count, 0)
        self.assertIsNone(user_vocabulary.last_practiced)

    def test_unique_constraint(self):
        UserVocabulary.objects.create(
            user=self.user,
            vocabulary=self.vocabulary,
        )

        with self.assertRaises(Exception):
            UserVocabulary.objects.create(
                user=self.user,
                vocabulary=self.vocabulary,
            )

    def test_mark_as_practiced(self):
        user_vocabulary = UserVocabulary.objects.create(
            user=self.user,
            vocabulary=self.vocabulary,
        )

        initial_count = user_vocabulary.practice_count
        initial_last_practiced = user_vocabulary.last_practiced

        user_vocabulary.mark_as_practiced()

        self.assertEqual(user_vocabulary.practice_count, initial_count + 1)
        self.assertIsNotNone(user_vocabulary.last_practiced)
        if initial_last_practiced is not None:
            self.assertGreater(user_vocabulary.last_practiced, initial_last_practiced)

    def test_mark_as_practiced_multiple_times(self):
        user_vocabulary = UserVocabulary.objects.create(
            user=self.user,
            vocabulary=self.vocabulary,
        )

        for _ in range(5):
            user_vocabulary.mark_as_practiced()

        self.assertEqual(user_vocabulary.practice_count, 5)

    def test_ready_for_practice(self):
        user_vocabulary = UserVocabulary.objects.create(
            user=self.user,
            vocabulary=self.vocabulary,
        )

        self.assertTrue(user_vocabulary.ready_for_practice)

        user_vocabulary.practice_count = 3
        user_vocabulary.last_practiced = timezone.now() - timezone.timedelta(days=4)
        user_vocabulary.save(update_fields=['practice_count', 'last_practiced'])

        self.assertTrue(user_vocabulary.ready_for_practice)

    def test_string_representation(self):
        user_vocabulary = UserVocabulary.objects.create(
            user=self.user,
            vocabulary=self.vocabulary,
        )

        expected = f"{self.user.username} - {self.vocabulary.word_vocab}"
        self.assertEqual(str(user_vocabulary), expected)

    def test_cascade_delete_user(self):
        user_vocabulary = UserVocabulary.objects.create(
            user=self.user,
            vocabulary=self.vocabulary,
        )

        user_vocabulary_id = user_vocabulary.id
        self.user.delete()

        self.assertFalse(UserVocabulary.objects.filter(id=user_vocabulary_id).exists())

    def test_cascade_delete_vocabulary(self):
        user_vocabulary = UserVocabulary.objects.create(
            user=self.user,
            vocabulary=self.vocabulary,
        )

        user_vocabulary_id = user_vocabulary.id
        self.vocabulary.delete()

        self.assertFalse(UserVocabulary.objects.filter(id=user_vocabulary_id).exists())
