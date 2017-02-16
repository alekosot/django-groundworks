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
