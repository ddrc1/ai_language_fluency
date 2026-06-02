"""
Tests for the english_practice module.
"""
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.language_practice.models import WordVocab, UserWordVocab


User = get_user_model()


class WordVocabModelTests(TestCase):
    """Test cases for the WordVocab model."""

    def setUp(self):
        """Set up test fixtures."""
        self.word_data = {
            'word_vocab': 'beautiful',
            'type': 'adjective',
            'definition': 'Bonito',
            'example': 'The sunset is beautiful.',
            'enable': True,
        }

    def test_create_word(self):
        """Test creating a new word."""
        word = WordVocab.objects.create(**self.word_data)
        
        self.assertIsNotNone(word.id)
        self.assertEqual(word.word_vocab, self.word_data['word_vocab'])
        self.assertEqual(word.type, self.word_data['type'])

    def test_word_duplicate_raises_error(self):
        """Test that duplicate words are not allowed."""
        WordVocab.objects.create(**self.word_data)
        
        with self.assertRaises(Exception):  # IntegrityError
            WordVocab.objects.create(**self.word_data)

    def test_word_string_representation(self):
        """Test string representation of word."""
        word = WordVocab.objects.create(**self.word_data)
        
        expected = f"{word.word_vocab} (Adjective)"
        self.assertEqual(str(word), expected)

    def test_word_enable_disable(self):
        """Test enabling and disabling words."""
        word = WordVocab.objects.create(**self.word_data)
        
        self.assertTrue(word.enable)
        
        word.enable = False
        word.save()
        
        self.assertFalse(word.enable)


class UserWordVocabModelTests(TestCase):
    """Test cases for the UserWordVocab model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.word = WordVocab.objects.create(
            word_vocab='serendipity',
            type='noun',
            definition='Encontro feliz por acaso',
            example='Meeting her was serendipity.',
            enable=True
        )

    def test_create_user_word(self):
        """Test creating a UserWordVocab relationship."""
        user_word = UserWordVocab.objects.create(
            user=self.user,
            word_vocab=self.word,
            level='learning'
        )
        
        self.assertIsNotNone(user_word.id)
        self.assertEqual(user_word.user, self.user)
        self.assertEqual(user_word.word_vocab, self.word)
        self.assertEqual(user_word.level, 'learning')

    def test_unique_constraint(self):
        """Test that user-word pairs are unique."""
        UserWordVocab.objects.create(
            user=self.user,
            word_vocab=self.word,
            level='learning'
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            UserWordVocab.objects.create(
                user=self.user,
                word_vocab=self.word,
                level='practicing'
            )

    def test_mark_as_practiced(self):
        """Test marking a word as practiced."""
        user_word = UserWordVocab.objects.create(
            user=self.user,
            word_vocab=self.word
        )
        
        initial_count = user_word.times_practiced
        initial_last_practiced = user_word.last_practiced
        
        user_word.mark_as_practiced()
        
        self.assertEqual(user_word.times_practiced, initial_count + 1)
        self.assertIsNotNone(user_word.last_practiced)
        self.assertGreater(user_word.last_practiced, initial_last_practiced or timezone.now() - timezone.timedelta(seconds=1))

    def test_mark_as_practiced_multiple_times(self):
        """Test marking a word as practiced multiple times."""
        user_word = UserWordVocab.objects.create(
            user=self.user,
            word_vocab=self.word
        )
        
        for _ in range(5):
            user_word.mark_as_practiced()
        
        self.assertEqual(user_word.times_practiced, 5)

    def test_update_level(self):
        """Test updating proficiency level."""
        user_word = UserWordVocab.objects.create(
            user=self.user,
            word_vocab=self.word,
            level='learning'
        )
        
        user_word.update_level('practicing')
        self.assertEqual(user_word.level, 'practicing')
        
        user_word.update_level('mastered')
        self.assertEqual(user_word.level, 'mastered')

    def test_update_level_invalid(self):
        """Test updating to an invalid level."""
        user_word = UserWordVocab.objects.create(
            user=self.user,
            word_vocab=self.word,
            level='learning'
        )
        
        original_level = user_word.level
        user_word.update_level('invalid_level')
        
        # Level should not change
        self.assertEqual(user_word.level, original_level)

    def test_string_representation(self):
        """Test string representation of UserWordVocab."""
        user_word = UserWordVocab.objects.create(
            user=self.user,
            word_vocab=self.word,
            level='learning'
        )
        
        expected = f"{self.user.username} - {self.word.word_vocab} (learning)"
        self.assertEqual(str(user_word), expected)

    def test_cascade_delete_user(self):
        """Test that UserWordVocab is deleted when user is deleted."""
        user_word = UserWordVocab.objects.create(
            user=self.user,
            word_vocab=self.word
        )
        
        user_word_id = user_word.id
        self.user.delete()
        
        self.assertFalse(UserWordVocab.objects.filter(id=user_word_id).exists())

    def test_cascade_delete_word(self):
        """Test that UserWordVocab is deleted when word is deleted."""
        user_word = UserWordVocab.objects.create(
            user=self.user,
            word_vocab=self.word
        )
        
        user_word_id = user_word.id
        self.word.delete()
        
        self.assertFalse(UserWordVocab.objects.filter(id=user_word_id).exists())
