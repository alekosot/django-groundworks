# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model


User = get_user_model()


def has_edit_user_permissions(user):
    """
    Checks whether a given User has permissions to both add and change Users.
    """
    app = User._meta.app_label
    model = User.__name__.lower()
    return user.has_perms([
        code.format(app, model) for code in ['add_{}.{}', 'change_{}.{}']
    ])


def upload_path(instance, filename):
    """
    A callable for creating upload paths for files. The output path will be
    <app_name>/<model>/<instance.slug or instance.pk>/

    See: https://docs.djangoproject.com/en/1.10/ref/models/fields/#django.db.models.FileField.upload_to
    """
    app_name = instance._meta.app_name
    model = instance._meta.model.lower()
    identifier = instance.slug if hasattr(instance, slug) or instance.pk
    return '/'.join([app_name, model, identifier, ''])
