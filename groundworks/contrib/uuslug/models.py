# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from uuslug import uuslug


@python_2_unicode_compatible
class UUSlugged(models.Model):
    """
    Adds a slug field, with a unique constraint and uses django-uuslug on it.
    """
    slug = models.SlugField(_('partial URL'), max_length=255, unique=True)

    _slug_source = 'title'  # A common case field, which is not given here.

    class Meta:
        abstract = True

    def generate_slug(self):
        return uuslug(getattr(self, self._slug_source), instance=self)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        return super(Slugged, self).save(*args, **kwargs)
