"""
Models for the login module.
"""
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser

from rest_framework_simplejwt.tokens import RefreshToken

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, username: str, password: str, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        
        if not username:
            raise ValueError('The given username must be set')

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, username: str, password: str=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email: str, username: str, password: str):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    email = models.EmailField(max_length=50, null=False, blank=False, unique=True)
    username = models.CharField(max_length=50, null=False, blank=False, unique=True)
    keep_sending_taks = models.BooleanField(default=True, help_text="Whether to keep sending practice words via email")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. '\
                                                         'Unselect this instead of deleting accounts.')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}
