# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, IntegrityError
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

    def generate_slug(self, source=''):
        if not source:
            source = getattr(self, self._slug_source)
        return uuslug(source, instance=self)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.slug:
                # A slug has been defined elsewhere, try to go with it
                try:
                    out = super(UUSlugged, self).save(*args, **kwargs)
                except IntegrityError:
                    # The slug is not unique, try to use it as a slug source
                    # for uuslug though, since it would be closer to the
                    # already defined slug.
                    self.slug = self.generate_slug(self.slug)
            else:
                self.slug = self.generate_slug()
        return super(UUSlugged, self).save(*args, **kwargs)
