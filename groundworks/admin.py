# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin, messages
from django.conf.urls import url
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.core.exceptions import PermissionDenied
from django.contrib.admin.options import IS_POPUP_VAR
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters

from groundworks.utils import has_edit_user_permissions

sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())

User = get_user_model()


class DifferentAddAndChangeAdmin(admin.ModelAdmin):
    """
    Inspired by django.contrib.auth.admin.UserAdmin, this provides different
    functionalities depending on whether the view is an "add" or a "change"
    one. The differences can be in ModelForm, fieldsets and/or inlines.
    """
    add_fieldsets = None
    add_form = None
    add_inlines = None

    def get_fieldsets(self, request, obj=None):
        """
        Use add_fieldsets during instance creation if it has been set.
        """
        if obj is None and self.add_fieldsets:
            return self.add_fieldsets
        return super(DifferentAddAndChangeAdmin, self) \
            .get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use add_form during instance creation if it has been set.
        """
        defaults = {}
        if obj is None and self.add_form:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(DifferentAddAndChangeAdmin, self) \
            .get_form(request, obj, **defaults)

    def add_view(self, *args, **kwargs):
        if self.add_inlines:
            self.inlines = self.add_inlines
        return super(DifferentAddAndChangeAdmin, self) \
            .add_view(*args, **kwargs)


class RelatedUserPasswordAdmin(admin.ModelAdmin):
    """
    Inspired by django.contrib.auth.admin.UserAdmin, this adds the
    functionality of changing the password of User through the change view
    of a related Model.

    Note that the relation must be either via aForeignKey or a OneToOne field,
    not a ManyToMany one.
    """
    change_user_password_template = None
    change_password_form = AdminPasswordChangeForm

    # Name of the field that holds the relation to User (ForeignKey, OneToOne)
    _user_rel_field = 'user'

    def lookup_allowed(self, lookup, value):
        # See #20078: we don't want to allow any lookups involving passwords.
        if lookup.startswith('password'):
            return False
        return super(RelatedUserPasswordAdmin, self) \
            .lookup_allowed(lookup, value)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request) \
                or not has_edit_user_permissions(request.user):
            raise PermissionDenied

        instance = self.get_object(request, unquote(id))
        if instance is None:
            raise Http404(_(
                '%(name)s object with primary key %(key)r does not exist.'
                ) % {
                'name': force_text(self.model._meta.verbose_name),
                'key': escape(id),
            })

        user = getattr(instance, self._user_rel_field)
        if user is None:
            raise Http404(_(
                '%(name)s object with primary key %(key)r is not related to '
                'any %(user)s.'
                ) % {
                'name': force_text(self.model._meta.verbose_name),
                'key': escape(id),
                'user': force_text(User._meta.verbose_name),
            })

        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(
                    request, form, None
                )
                self.log_change(request, user, change_message)
                msg = ugettext('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            instance._meta.app_label,
                            instance._meta.model_name,
                        ),
                        args=(instance.pk,),
                    )
                )
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(self.admin_site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context,
        )

    def get_urls(self):
        return [
            url(
                r'^(.+)/password/$',
                self.admin_site.admin_view(self.user_change_password),
                name='user_password_change',
            ),
        ] + super(RelatedUserPasswordAdmin, self).get_urls()
