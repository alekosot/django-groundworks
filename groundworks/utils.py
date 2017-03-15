# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.utils.encoding import force_text


def has_edit_user_permissions(user):
    """
    Checks whether a given User has permissions to both add and change Users.
    """
    User = get_user_model()
    app = User._meta.app_label
    model = User.__name__.lower()
    return user.has_perms([
        code.format(app, model) for code in ['add_{}.{}', 'change_{}.{}']
    ])


def upload_path(instance, filename):
    """
    A callable for creating upload paths for files. The output path will be
    <app_label>/<model>/<instance.pk>/filename

    See: https://docs.djangoproject.com/en/1.10/ref/models/fields/#django.db.models.FileField.upload_to
    """
    app_name = instance._meta.app_label
    model = instance._meta.model.__name__.lower()
    identifier = force_text(instance.pk)
    return '/'.join([app_name, model, identifier, filename])
