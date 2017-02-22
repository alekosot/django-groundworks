# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth import get_user_model
from django.utils import six
from django.utils.translation import ugettext_lazy as _


User = get_user_model()


class UserFieldsIncludedMixin(forms.ModelForm):
    """
    Used for editing User instances from a ModelForm of an instance that has a
    ForeignKey or a OneToOne relation to User.

    This is for UX reasons mostly, so that regular users can use a single form
    to edit the related model and the User. Therefore, all permission related
    stuff are omitted from the form. In other words, this is designed to
    complement the standard User workflow and not to replace it.
    """
    _user = None   # Holds the related User instance
    _user_password_field = 'password'   # Name of the password field for User
    # Name of the field that holds the relation to User (ForeignKey, OneToOne)
    _user_rel_field = 'user'
    # The name of the fields that you wish to fetch from the related User.
    # Note that you have to add the actual fields yourself.
    _user_fields = []

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        if instance and instance.pk:
            self._user = getattr(instance, self._user_rel_field),
            # HACK: For some peculiar reason the line above returns a tuple!!!
            #       Obviously this indicates an error. The hack below counters
            #       it, but still it's worth to keep it in mind.
            self._user = self._user[0]
            kwargs.update(initial={field: getattr(self._user, field)
                                   for field in self._user_fields})
        else:
            self._user = User()

        super(UserFieldsIncludedMixin, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(UserFieldsIncludedMixin, self) \
            .save(commit=False)
        data = self.cleaned_data

        for field in self._user_fields:
            setattr(self._user, field, data[field])

        if self._user_password_field in self._user_fields:
            self._user.set_password(
                self.cleaned_data[self._user_password_field]
            )

        # NOTE: Since django 1.8+ does not allow the relation to unsaved
        #       models, we save the User instance before assigning it to the
        #       relative field. This is a bit counterintuitive when commit is
        #       False, but it seems to be a necessary evil.
        self._user.save()
        setattr(instance, self._user_rel_field, self._user)

        if commit:
            instance.save()

        return instance


class MultiSourceFieldsFormMixin(object):
    """
    A hackish way to provide multiple fields (sources) from which to derive
    the value of another field (target). The value of only one source field
    is acceptable for any given target field.

    This is usually used with a hidden "target" field, that is not required,
    so that it's value is gotten from the source fields.

    Note that this does not know how to handle the initial value for the fields
    in question and you have to implement your own logic for this in the
    ``set_initial_for_multi_source_field`` method.

    This is an anti-pattern basically, because django handles this with
    ``MultiWidget``s normally. Therefore, the use of this is discouraged.
    """
    _normalized_multi_source_data = {}

    def __init__(self, *args, **kwargs):
        super(MultiSourceFieldsFormMixin, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        if instance and instance.pk:
            self.set_initial_for_multi_source_field()

    def set_initial_for_multi_source_field(self):
        raise NotImplementedError(
            'Method set_initial_for_multi_source_field has not been '
            'implemented for {}.'.format(self.__class__.__name__))

    def clean(self):
        """
        Check that for every target field, only one source field has a value
        and if so normalize its data by calling ``normalize_multi_source_data``
        on it.
        """
        cleaned_data = super(MultiSourceFieldsFormMixin, self).clean()
        for target, sources in six.iteritems(self._multi_source_fields):
            data = [cleaned_data[s] for s in sources]
            non_empty_data = [d for d in filter(None, data)]
            if len(non_empty_data) != 1:
                raise forms.ValidationError(_(
                    'Please provide one (and only one) of {}'.format(
                        ', '.join(self[f].label for f in sources)
                    )
                ))
            self.store_normalized_multi_source_data(
                target, non_empty_data[0]
            )
        return cleaned_data

    def save(self, commit=True):
        instance = super(MultiSourceFieldsFormMixin, self).save(commit=False)
        for field, value in six.iteritems(self._normalized_multi_source_data):
            setattr(instance, field, value)
        instance.save()
        return instance

    def store_normalized_multi_source_data(self, target_field, source_data):
        """
        Caches the cleaned data of a source field, appropriately normalized
        for later commiting to the persistence level (i.e. database) via
        ``save``.
        """
        self._normalized_multi_source_data[target_field] = source_data

    @property
    def _multi_source_fields(self):
        """
        This should be overriden by subclasses, normally via an attribute of
        the class.
        """
        raise NotImplementedError(
            '{}._multi_source_fields has not been set'
            .format(self.__class__.__name__)
        )
