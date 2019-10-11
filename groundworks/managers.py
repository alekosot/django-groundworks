# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

from django.db import models
from django.utils import timezone


class ActivatableQuerySet(models.QuerySet):
    """
    A ``QuerySet`` for ``Activatable`` models
    """
    def active(self):
        return self.filter(is_active=True)


class ActivatableManager(models.Manager):
    """
    A ``Manager`` for ``Activatable`` models
    """
    def get_queryset(self):
        return ActivatableQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()


class TimeStampedQuerySet(models.QuerySet):
    """
    A ``QuerySet`` for ``TimeStamped`` models.
    """

    def newest(self):
        return self.order_by('-date_created')


class TimeStampedManager(models.Manager):
    """
    A ``Manager`` for ``TimeStamped`` models.
    """

    def get_queryset(self):
        return TimeStampedQuerySet(self.model, using=self._db)

    def newest(self):
        return self.get_queryset().newest()


class PublishableQuerySet(models.QuerySet):
    """
    A ``QuerySet`` for ``Publishable`` models.
    """

    def draft(self):
        now = timezone.now()
        return self.filter(
            models.Q(is_published=False) | models.Q(date_published__gt=now)
        )

    def published(self):
        now = timezone.now()
        return self.filter(is_published=True, date_published__lte=now)

    def published_before(self, date):
        return self.filter(publish_date__lt=date)

    def published_after(self, date):
        return self.filter(publish_date__gt=date)

    def published_between(self, start, end):
        return self.filter(publish_date__range=(start, end))


class PublishableManager(models.Manager):
    """
    A ``Manager`` for ``Publishable`` models.
    """

    def get_queryset(self):
        return PublishableQuerySet(self.model, using=self._db)

    def draft(self):
        return self.get_queryset().draft()

    def published(self):
        return self.get_queryset().published()

    def published_before(self, date):
        return self.get_queryset().published_before(date)

    def published_after(self, date):
        return self.get_queryset().published_after(date)

    def published_between(self, start, end):
        return self.get_queryset().published_between(start, end)

class UndeletableQuerySet(models.QuerySet):
    """
    A ``QuerySet`` for ``Undeletable`` models.
    """

    def deleted(self):
        return self.exclude(date_deleted__isnull=True)

    def not_deleted(self):
        return self.filter(date_deleted__isnull=True)


class UndeletableManager(models.Manager):
    """
    A ``Manager`` for ``Undeletable`` models.
    """

    # NOTE: Do not filter out the deleted objects in get_queryset. This
    #       manager is set as the base_manager for reverse relations as well,
    #       so filtering should not take place here. See the docs on Managers
    #       and base_managers.
    def get_queryset(self):
        return UndeletableQuerySet(self.model, using=self._db)

    def deleted(self):
        return self.get_queryset().deleted()

    def not_deleted(self):
        return self.get_queryset().not_deleted()


class RandomizingManager(models.Manager):
    def _get_pool_for_random(self):
        """
        Provides the initial pool of instances that ``get_random`` will return
        instances from.
        """
        return self.get_queryset().distinct('pk')

    def get_random(self, count):
        """
        Returns random instances for the managed Model from a sample pool of
        instances. The sample pool is the *sequence* returned from
        ``get_pool_for_random``. The amount is equal to count if there are
        enough instances in the sample pool.
        """
        choices = []
        pool = set(self._get_pool_for_random())
        while count:
            try:
                choices = random.sample(pool, count)
            except ValueError:  # Not enough instances to fetch
                count -= 1
            else:
                break
        return choices
