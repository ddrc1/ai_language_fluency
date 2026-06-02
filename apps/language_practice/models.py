import os
from dotenv import load_dotenv

from django.utils import timezone
from django.db import models

from apps.authentication.models import User

load_dotenv()

PRACTINCING_FACTOR = float(os.getenv("PRACTINCING_FACTOR", 2))


class Vocabulary(models.Model):    
    word_vocab = models.CharField(max_length=255, unique=True, blank=False, null=False,help_text="The word or expression to practice")
    language = models.TextField(blank=False, null=False, unique=True, help_text="The language of the word (e.g., 'English', 'Spanish')")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enable = models.BooleanField(default=True, help_text="Whether this word is available for practice")

    def __str__(self):
        return self.word_vocab


class UserVocabulary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='words_vocab', help_text="The user practicing this word")
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE, related_name='users', help_text="The vocabulary word being practiced")
    practice_count = models.PositiveIntegerField(default=0, help_text="Number of times the user has practiced this word")
    last_practiced = models.DateTimeField(blank=True, null=True, help_text="Last time the user practiced this word")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enable = models.BooleanField(default=True, help_text="Whether this user-word association is active")


    class Meta:
        verbose_name = 'User Vocabulary'
        verbose_name_plural = 'Users Vocabulary'
        unique_together = ('user', 'vocabulary')

    def __str__(self):
        return f"{self.user.username} - {self.vocabulary.word_vocab}"

    def mark_as_practiced(self):
        """
        Update the practice count and timestamp.
        """
        
        self.practice_count += 1
        self.last_practiced = timezone.now()
        self.save()

    @property
    def ready_for_practice(self) -> bool:
        """
        Check if the word is ready for practice using spaced repetition.
        Uses exponential backoff: interval doubles with each practice.
        """
        if self.last_practiced is None:
            return True
        
        days_since = (timezone.now() - self.last_practiced).days
        
        interval = PRACTINCING_FACTOR ** (self.practice_count - 1) if self.practice_count > 0 else 0
        
        return days_since >= interval
