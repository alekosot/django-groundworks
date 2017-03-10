# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals

from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def naive_i18n_url(context, lang):
    """
    Returns the current url path with the language changed to the lang given.

    This is done in a very naive manner, with the assumption that the current
    url corresponds to the format of django's i18n_patterns (i.e. /en/about/,
    /jp/about/, etc). Note also that **no check at all** is done on the lang
    passed to it, which is your responsibility.
    """
    path_parts = context['request'].path.split('/')
    path_parts[1] = lang
    return '/'.join(path_parts)
