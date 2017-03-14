# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from ckeditor_uploader.fields import RichTextUploadingField


class RichText(models.Model):
    content = RichTextUploadingField(_('content'), blank=True)

    class Meta:
        abstract = True
