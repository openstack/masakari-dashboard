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
from django.utils.translation import ungettext_lazy

from horizon import exceptions
from horizon import tables

from masakaridashboard.api import api


HOST_FILTER_CHOICES = (
    ('failover_segment_id', _("Segment Id ="), True),
    ('type', _("Type ="), True),
    ('on_maintenance', _("On Maintenance ="), True),
    ('reserved', _("Reserved ="), True),
)


class HostFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = HOST_FILTER_CHOICES


class DeleteHost(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Host",
            u"Delete Hosts",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Host",
            u"Deleted Hosts",
            count
        )

    def delete(self, request, data):
        row_data = data.split(',')
        segment_uuid = row_data[1]
        host_uuid = row_data[0]
        try:
            api.delete_host(request, host_uuid, segment_uuid)
        except Exception:
            msg = _('Unable to delete host.')
            redirect = reverse('horizon:masakaridashboard:hosts:index')
            exceptions.handle(self.request, msg, redirect=redirect)


class UpdateHost(tables.LinkAction):

    name = "update"
    verbose_name = _("Update Host")
    classes = ("ajax-modal",)

    def get_link_url(self, datum):
        host_id = datum.uuid + ',' + datum.failover_segment_id
        url = "horizon:masakaridashboard:hosts:update"
        return reverse(url, args=[host_id])


class HostTable(tables.DataTable):

    name = tables.Column('name', verbose_name=_("Name"),
                         link="horizon:masakaridashboard:hosts:detail")
    uuid = tables.Column('uuid', verbose_name=_("UUID"))
    reserved = tables.Column(
        'reserved', verbose_name=_("Reserved"))
    type = tables.WrappingColumn('type', verbose_name=_("Type"))
    control_attributes = tables.Column(
        'control_attributes', verbose_name=_(
            "Control Attribute"), truncate=40)
    on_maintenance = tables.Column(
        'on_maintenance', verbose_name=_("On Maintenance"))
    failover_segment_id = tables.Column(
        'failover_segment_id', verbose_name=_("Failover Segment"),
        link="horizon:masakaridashboard:segments:detail")

    def get_object_id(self, datum):
        return datum.uuid + ',' + datum.failover_segment_id

    class Meta(object):
        name = "host"
        verbose_name = _("Host")
        table_actions = (HostFilterAction, DeleteHost)
        row_actions = (UpdateHost,)
