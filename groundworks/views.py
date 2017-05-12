# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.base import TemplateView
from groundworks.response import (
    TemplateBadRequestResponse, TemplateForbiddenResponse,
    TemplateNotFoundResponse, TemplateServerErrorResponse
)


class BadRequestView(TemplateView):
    """
    A class based view for use as a handler400.
    """
    template_name = "400.html"
    response_class = TemplateBadRequestResponse


class ForbiddenView(TemplateView):
    """
    A class based view for use as a handler402.
    """
    template_name = "402.html"
    response_class = TemplateForbiddenResponse


class NotFoundView(TemplateView):
    """
    A class based view for use as a handler404.
    """
    template_name = "404.html"
    response_class = TemplateNotFoundResponse


class ServerErrorView(TemplateView):
    """
    A class based view for use as a handler500.
    """
    template_name = "500.html"
    response_class = TemplateServerErrorResponse
