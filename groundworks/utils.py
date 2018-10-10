# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from django.utils.text import slugify
from django.utils import timezone


def has_edit_user_permissions(user):
    """
    Checks whether a given User has permissions to both add and change Users.
    """
    User = get_user_model()
    app = User._meta.app_label
    model = User.__name__.lower()
    perms = [code.format(app, model) for code in ['{}.add_{}', '{}.change_{}']]
    return user.has_perms(perms)


def upload_path(instance, filename):
    """
    A callable for creating upload paths for files. The output path will be
    <year>/<month>/<day>/<smart_filename__with_random_bit>

    NOTE: This depends on the ``unidecode`` python library

    See: https://docs.djangoproject.com/en/1.10/ref/models/fields/#django.db.models.FileField.upload_to
    """
    from unidecode import unidecode

    _filename, ext = filename.rsplit('.', 1)
    _random, __ = force_text(uuid.uuid4()).split('-', 1)

    now = timezone.now()
    year = force_text(now.year)
    month = force_text(now.month)
    day = force_text(now.day)

    subject = ''
    for attr in ('title', 'name', 'slug' 'caption'):
        try:
            subject = getattr(instance, attr)
        except AttributeError:
            pass
        else:
            break
    if not subject:
        subject = _filename
    subject = unidecode(subject)
    subject = slugify(subject)
    subject = subject[:20]
    subject.rstrip('-')

    subject = '_'.join([subject, _random])
    new_filename = '.'.join([subject, ext])

    return '/'.join([year, month, day, new_filename])
