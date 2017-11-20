# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse_lazy
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils import six, timezone

from groundworks import managers


class TimeStamped(models.Model):
    date_created = models.DateTimeField(_('date created'))
    date_updated = models.DateTimeField(
        _('date updated'), default=timezone.now)

    objects = managers.TimeStampedManager()

    class Meta:
        abstract = True
        base_manager_name = 'objects'

    def save(self, *args, **kwargs):
        if not self.date_created:
            self.date_created = timezone.now()
        return super(TimeStamped, self).save(*args, **kwargs)


class Publishable(models.Model):
    date_published = models.DateTimeField(
        _('published on'), blank=True, null=True, help_text=_(
            'This will not be shown until the date and time given here.'))
    is_published = models.BooleanField(
        _('Published'), default=False, help_text=_(
            'This will not be shown publicly if this is unchecked.'))

    objects = managers.PublishableManager()

    class Meta:
        abstract = True
        base_manager_name = 'objects'

    def is_draft(self, datetime=None):
        """
        Check if this is draft for this datetime (or at the time of the call).
        """
        if not self.date_published:
            return True
        else:
            datetime = datetime or timezone.now()
            return self.date_published > datetime


class WithMetadata(models.Model):
    meta_title = models.CharField(
        _('meta title'), blank=True, max_length=140,
        help_text=_('This cannot be more than 140 characters.'))
    meta_description = models.TextField(
        _('meta description'), blank=True, max_length=160,
        help_text=_('This cannot be more than 160 characters.'))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.meta_description = self.generate_meta_description()
        return super(WithMetadata, self).save(*args, **kwargs)

    def generate_meta_description(self):
        return self.meta_description


class Undeletable(models.Model):
    """
    Replaces deletion of this model with updating of date_deleted.

    NOTE: The instances can be normally deleted via Managers.
    """
    date_deleted = models.DateTimeField(blank=True)

    objects = managers.UndeletableManager()

    class Meta:
        abstract = True
        base_manager_name = 'objects'

    def delete(self, *args, **kwargs):
        self.date_deleted = timezone.now()
        return


# TODO: Add check for the case of unique=True for a field in
#       _enforced_values, while the corresponding value is not a callable.
class WithEnforcedValues(models.Model):
    """
    Enforces values for fields before save. The fields are defined as keys in
    the _enforced_values dictionary and the values are defined as values for
    the appropriate. If the value is callable it will be called with the
    specific instance as the only parameter.

    Example:
        class ModelA(models.Model):
            field1 = models.CharField(...)
            field2 = models.CharField(...)

        _enforced_values = {
            'field1': 'this value is enforced for every ModelA.field1'
            'field2': callable
        }
    """
    _enforced_values = {}

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._enforced_values:
            for field, value in six.iteritems(self._enforced_values):
                if callable(value):
                    setattr(self, field, value(self))
                setattr(self, field, value)
        return super(WithEnforcedValues, self).save(*args, **kwargs)


class RegisteredInAdmin(models.Model):
    """
    Abstraction for ``Model``s registered in the django's admin site.
    """

    class Meta:
        abstract = True

    def get_admin_url(self):
        """
        Return the absolute url of this ``Model`` instance in the admin site
        of Django.

        If this instance has not been saved to the database yet, return the
        ``add`` view for this Model, otherwise return the ``change`` view.

        NOTE: This assumes that the url names and namespace are the ones given
        in the docs.
        """
        url_name = 'admin:{}_{}'.format(
            self._meta.app_label,
            self._meta.model_name
        )
        if self.pk:
            url_name += '_change'
            url = reverse_lazy(url_name, args=(self.pk,))
        else:
            url_name += '_add'
            url = reverse_lazy(url_name)
        return url
