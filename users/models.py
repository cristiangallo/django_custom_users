# -*- coding: UTF-8 -*-

"""
:author: Cristián M. Gallo (mail@cristiangallo.com.ar)
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(
            self, email, password=None, is_active=True, is_staff=False, is_superuser=False):
        from django.utils.translation import gettext_lazy as _

        if not email:
            raise ValueError(_('Users must have an email address'))
        if not password:
            raise ValueError(_('Users must have a password'))

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_active = is_active
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, password):
        """
        Creates a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        return user


class User(AbstractBaseUser, PermissionsMixin):
    from django.contrib.auth.validators import UnicodeUsernameValidator
    from sorl.thumbnail import ImageField as sorl_thumbnail_ImageField

    username_validator = UnicodeUsernameValidator()
    email = models.EmailField(
        verbose_name=_('email address'),
        max_length=255,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
    profile_image = sorl_thumbnail_ImageField(max_length=255, upload_to="profile-images/", null=True, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def adm_thumb_image(self):
        from django.utils.safestring import mark_safe
        from sorl.thumbnail import get_thumbnail
        try:
            return mark_safe('<img src="%s" />' % get_thumbnail(
                self.profile_image, "100x100", crop='center', quality=95).url)
        except:
            return ""
    adm_thumb_image.short_description = 'Imagen de perfil'
