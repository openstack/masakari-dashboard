# Copyright(c) 2022 Inspur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.utils.translation import gettext_lazy as _

from horizon import tables


VMOVE_FILTER_CHOICES = (
    ('notification_uuid', _("Notification UUId ="), True),
    ('type', _("Type ="), True),
    ('status', _("Status ="), True),
)


class VMoveFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = VMOVE_FILTER_CHOICES


class VMoveTable(tables.DataTable):

    uuid = tables.Column('uuid', verbose_name=_("UUID"),
                         link="horizon:masakaridashboard:vmoves:detail")
    notification_id = tables.Column(
        'notification_id', verbose_name=_("Notification UUID"),
        link="horizon:masakaridashboard:notifications:detail")
    server_id = tables.Column(
        'server_id', verbose_name=_("Server ID"))
    server_name = tables.Column(
        'server_name', verbose_name=_("Server Name"))
    type = tables.Column('type', verbose_name=_("Type"))
    source_host = tables.Column(
        'source_host', verbose_name=_("Source Host"))
    dest_host = tables.Column(
        'dest_host', verbose_name=_("Dest Host"))
    start_time = tables.Column(
        'start_time', verbose_name=_("Start Time"))
    end_time = tables.Column(
        'end_time', verbose_name=_("End Time"))
    status = tables.Column(
        'status', verbose_name=_("Status"))

    def get_object_id(self, datum):
        return datum.notification_id + ',' + datum.uuid

    class Meta(object):
        name = "vmove"
        verbose_name = _("VMove")
        table_actions = (VMoveFilterAction,)
