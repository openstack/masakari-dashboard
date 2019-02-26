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

from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.utils import filters


NOTIFICATION_FILTER_CHOICES = (
    ('source_host_uuid', _("Source Host UUID ="), True),
    ('type', _("Type ="), True),
    ('status', _("Status ="), True),
    ('generated_since', _("Generated Since ="), True),
)


class NotificationFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = NOTIFICATION_FILTER_CHOICES


class ProgressDetailsItem(object):
    def __init__(self, id, action, timestamp, message):

        self.id = id
        self.action = action
        self.timestamp = timestamp
        self.message = message


class NotificationsTable(tables.DataTable):

    source_host_uuid = tables.Column(
        'source_host_uuid', verbose_name=_("Host"))
    notification_uuid = tables.Column(
        'notification_uuid', verbose_name=_("UUID"),
        link="horizon:masakaridashboard:notifications:detail")
    type = tables.Column('type', verbose_name=_("Type"))
    status = tables.Column('status', verbose_name=_("Status"))
    payload = tables.Column(
        'payload', verbose_name=_("Payload"), truncate=40)

    def get_object_id(self, datum):
        return datum.notification_uuid

    class Meta(object):
        name = "notifications"
        verbose_name = _("Notifications")
        table_actions = (NotificationFilterAction,)


class NotificationProgressDetailsTable(tables.DataTable):

    action = tables.Column('action', verbose_name=_('Action'))
    timestamp = tables.Column('timestamp', verbose_name=_('Timestamp'),
                              filters=[filters.parse_isotime])
    message = tables.Column('message', verbose_name=_('Message'))
    id = tables.Column('id', verbose_name=_('ID'), hidden=True)

    class Meta(object):
        name = "notification_progress_details"
        verbose_name = _("NotificationProgressDetails")
