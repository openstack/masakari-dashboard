# Copyright (c) 2018 NTT DATA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from masakaridashboard.api import api


class UpdateHostForm(forms.SelfHandlingForm):

    uuid = forms.CharField(widget=forms.HiddenInput())
    failover_segment_id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(
        label=_('Host Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    reserved = forms.ChoiceField(
        label=_('Reserved'),
        choices=[('False', 'False'),
                 ('True', 'True')],
        widget=forms.Select(
            attrs={'class': 'switchable',
                   'data-slug': 'available host'}),
        required=False)
    type = forms.CharField(
        label=_('Type'),
        widget=forms.TextInput(attrs={'maxlength': 255}))
    control_attributes = forms.CharField(
        label=_('Control Attribute'),
        widget=forms.TextInput())
    on_maintenance = forms.ChoiceField(
        label=_('On Maintenance'),
        choices=[('False', 'False'),
                 ('True', 'True')],
        widget=forms.Select(
            attrs={'class': 'switchable',
                   'data-slug': 'available host'}),
        required=False
    )

    def handle(self, request, data):
        try:
            attrs = {'name': data['name'],
                     'reserved': data['reserved'],
                     'type': data['type'],
                     'control_attributes': data['control_attributes'],
                     'on_maintenance': data['on_maintenance']}
            api.update_host(request, data['uuid'],
                            data["failover_segment_id"], attrs)
            msg = _('Successfully updated host.')
            messages.success(request, msg)
        except Exception:
            msg = _('Failed to update host.')
            redirect = reverse('horizon:masakaridashboard:hosts:index')
            exceptions.handle(request, msg, redirect=redirect)
        return True
