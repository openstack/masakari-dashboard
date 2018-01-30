# Copyright (C) 2018 NTT DATA
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from masakaridashboard.api import api


class CreateSegmentForm(forms.SelfHandlingForm):
    name = forms.CharField(
        label=_('Segment Name'),
        widget=forms.TextInput(attrs={'maxlength': 255}),
        help_text=_('The segment name.'))
    recovery_method = forms.ChoiceField(
        label=_('Recovery Method'),
        choices=[('auto', 'auto'),
                 ('auto_priority', 'auto_priority'),
                 ('reserved_host', 'reserved_host'),
                 ('rh_priority', 'rh_priority')],
        widget=forms.Select(
            attrs={'class': 'switchable',
                   'data-slug': 'recovery_method'}),
        required=True,
        help_text=_('Type of recovery if any host in this segment goes down.')
    )
    service_type = forms.CharField(
        label=_('Service Type'),
        help_text=_('The name of service which will be deployed in this'
                    ' segment. As of now user can mention COMPUTE as service'
                    ' type.'),
        widget=forms.TextInput(attrs={
            'readonly': 'readonly', 'value': 'compute'}))
    description = forms.CharField(
        label=_("Description"), widget=forms.Textarea(
            attrs={'rows': 4}), required=False)

    def __init__(self, *args, **kwargs):
        super(CreateSegmentForm, self).__init__(*args, **kwargs)

    def handle(self, request, data):
        try:
            api.segment_create(request, data)
            msg = _('Successfully created segment')
            messages.success(request, msg)
        except Exception as exc:
            if exc.status_code == 409:
                msg = _('Segment with name "%s" already exists') % data["name"]
            else:
                msg = _('Failed to create segment')
            redirect = reverse('horizon:masakaridashboard:segments:index')
            exceptions.handle(request, msg, redirect=redirect)
        return True


class UpdateForm(forms.SelfHandlingForm):
    uuid = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(
        label=_('Segment Name'),
        widget=forms.TextInput(attrs={'maxlength': 255}))
    recovery_method = forms.ChoiceField(
        label=_('Recovery Method'),
        choices=[('auto', 'auto'),
                 ('auto_priority', 'auto_priority'),
                 ('reserved_host', 'reserved_host'),
                 ('rh_priority', 'rh_priority')],
        widget=forms.Select(
            attrs={'class': 'switchable',
                   'data-slug': 'recovery_method'}),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        widget=forms.Textarea(
            attrs={'width': "100%", 'cols': "80", 'rows': "5", }),
        required=False
    )

    def handle(self, request, data):
        try:
            fields_to_update = {'name': data['name'],
                                'recovery_method': data['recovery_method'],
                                'description': data['description']}
            api.segment_update(request, data['uuid'], fields_to_update)
            msg = _('Successfully updated segment.')
            messages.success(request, msg)
        except Exception:
            msg = _('Failed to update segment.')
            redirect = reverse('horizon:masakaridashboard:segments:index')
            exceptions.handle(request, msg, redirect=redirect)

        return True
