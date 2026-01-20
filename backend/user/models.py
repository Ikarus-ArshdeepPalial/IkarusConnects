"""Custom User model and Manager"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required")
        if not username:
            raise ValueError("Username required")

        user = self.model(
            email=self.normalize_email(email), username=username, **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, username, password=None):
        if not email:
            raise ValueError("Email required")
        if not username:
            raise ValueError("Username required")

        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self.db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True, max_length=255)
    name = models.CharField(max_length=255, default="First Last Name")

    username = models.CharField(unique=True, max_length=30)
    bio = models.CharField(
        max_length=300, null=True, default="Hello i am using collabus"
    )

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    last_visit = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    private_account = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username
