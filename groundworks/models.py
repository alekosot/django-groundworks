# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

try:
    from uuslug import uuslug
except ImportError:
    from django.utils.text import slugify

    def uuslug(string, obj):
        return slugify(string)

try:
    from ckeditor_uploader.fields import RichTextUploadingField
except:
    from django.forms import TextField as RichTextUploadingField


@python_2_unicode_compatible
class TimeStamped(models.Model):
    date_created = models.DateTimeField(_('date created'))
    date_updated = models.DateTimeField(
        _('date updated'), default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.date_created:
            self.date_created = timezone.now()
        return super(TimeStamped, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Publishable(models.Model):
    date_published = models.DateTimeField(
        _('published on'), blank=True, null=True, help_text=_(
            'This will not be shown until the date and time given here.'))
    is_published = models.BooleanField(
        _('Is this published?'), default=False, help_text=_(
            'This will not be shown if this is unchecked.'))

    class Meta:
        abstract = True

    @property
    def is_draft(self):
        if not self.date_published:
            return True
        else:
            return self.date_published > timezone.now()

    @property
    def is_published(self):
        return not self.is_draft


@python_2_unicode_compatible
class Slugged(models.Model):
    """
    Adds a slug field, with a unique constraint, but does nothing to ensure it.
    """
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('partial URL'), max_length=255, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def generate_slug(self):
        return uuslug(self.title, instance=self)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        return super(Slugged, self).save(*args, **kwargs)


class WithMetaData(models.Model):
    meta_title = models.CharField(_('meta title'), blank=True, max_length=255)
    meta_description = models.TextField(
        _('meta description'), blank=True, max_length=160, help_text=_(
            'Normally you should keep this between 150 and 160 characters'))
    meta_keywords = models.CharField(
        _('meta keywords'), blank=True, help_text=(
            'Keep in mind to use commas inbetween keywords and key phrases.'))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.meta_description = self.generate_meta_description()
        return super(WithMetaData, self).save(*args, **kwargs)

    def generate_meta_description(self):
        return self.meta_description


class RichText(models.Model):
    content = RichTextUploadingField(_('content'), )

    class Meta:
        abstract = True


class Undeletable(models.Model):
    """
    Replaces deletion of this model with updating of date_deleted.

    NOTE: The instances can be normally deleted via Managers.
    """
    date_deleted = models.DateTimeField(blank=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        return
