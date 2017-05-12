# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.response import TemplateResponse
from django.http.response import (
    HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound,
    HttpResponseServerError
)


class TemplateBadRequestResponse(HttpResponseBadRequest, TemplateResponse):
    pass


class TemplateForbiddenResponse(HttpResponseForbidden, TemplateResponse):
    pass


class TemplateNotFoundResponse(HttpResponseNotFound, TemplateResponse):
    pass


class TemplateServerErrorResponse(HttpResponseServerError, TemplateResponse):
    pass
