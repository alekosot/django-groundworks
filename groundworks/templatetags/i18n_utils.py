# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals

from django import template
from django.conf import settings
from django.utils.translation import (
    get_language_from_request,
    get_language_info,
    get_language
)


register = template.Library()


@register.simple_tag(takes_context=True)
def naive_i18n_url(context, lang, unprefixed_default_language=False):
    """
    Returns the current url path with the language changed to the lang given.

    Set ``unprefixed_default_language`` to a truthy value in order for this to
    work with the ``prefix_default_language=False`` option of
    ``i18n_patterns``.

    This is done in a very naive manner, with the assumption that the current
    url corresponds to the format of django's i18n_patterns (i.e. /en/about/,
    /jp/about/, etc). Note also that **no check at all** is done on the lang
    passed to it, which is your responsibility.
    """
    path_parts = context['request'].path.split('/')
    current = get_language()
    if unprefixed_default_language and current != settings.LANGUAGE_CODE:
        path_parts.pop(1)
    if not (lang == settings.LANGUAGE_CODE and unprefixed_default_language):
        path_parts.insert(1, lang)
    return '/'.join(path_parts)


@register.simple_tag(takes_context=True)
def sorted_languages_info(context, check_path=True):
    """
    Wrapper around django's ``get_language_info`` i18n utility, that returns
    the "info" for all languages given in settings.LANGUAGES, with the
    active one being first. The identification of the current language is done
    with the use of ``get_language_from_request``, which is passed the
    ``check_path`` parameter.

    Usage::

        {% sorted_languages_info as langs %}
        {% for l in langs %}
            {{ l.code }}
            {{ l.name }}
            {{ l.name_translated }}
            {{ l.name_local }}
            {{ l.bidi|yesno:"bi-directional,uni-directional" }}
        {% endfor %}
    """
    langs = [_lang[0] for _lang in settings.LANGUAGES]
    current_lang = get_language_from_request(context['request'], check_path)
    langs.remove(current_lang)
    langs.insert(0, current_lang)
    return [get_language_info(lang) for lang in langs]
