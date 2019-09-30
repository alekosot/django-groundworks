# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals

import unicodedata

from django import template
from django.conf import settings
from django.urls import translate_url
from django.utils.encoding import force_text
from django.utils.translation import get_language_info, get_language


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
    if (unprefixed_default_language and current != settings.LANGUAGE_CODE)  \
            or not unprefixed_default_language:
        path_parts.pop(1)
    if not (lang == settings.LANGUAGE_CODE and unprefixed_default_language)  \
            or not unprefixed_default_language:
        path_parts.insert(1, lang)
    return '/'.join(path_parts)


@register.simple_tag(takes_context=True)
def sorted_languages_info(context):
    """
    Wrapper around django's ``get_language_info`` i18n utility, that returns
    the "info" for all languages given in settings.LANGUAGES, with the
    active one being first.

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
    current_lang = get_language()
    langs.remove(current_lang)
    langs.insert(0, current_lang)
    return [get_language_info(lang) for lang in langs]


@register.filter
def strip_accents(obj):
    """
    Return ``obj`` as a string (or unicode in Python2) with its accents
    removed.
    """
    string = force_text(obj)
    accentless_chars = [c for c in unicodedata.normalize('NFD', string)
                        if unicodedata.category(c) != 'Mn']
    return ''.join(accentless_chars)


@register.simple_tag(takes_context=True)
def translate_current_url(context, lang):
    query = ''
    url = context['request'].get_full_path()
    if '?' in url:
        url, query = url.split('?')
    else:
        url = url

    url = translate_url(url, lang)
    url = url + '?' + query if query else url

    return url


@register.simple_tag
def absolute_url_for_lang(obj, lang):
    return obj.get_absolute_url_for_lang(lang)
