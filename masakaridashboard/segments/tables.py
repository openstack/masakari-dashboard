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
from django.utils.translation import ungettext_lazy

from masakaridashboard.api import api

from horizon import tables


class CreateSegment(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Segment")
    url = "horizon:masakaridashboard:segments:create_segment"
    classes = ("ajax-modal",)
    icon = "plus"


SEGMENT_FILTER_CHOICES = (
    ('recovery_method', _("Recovery Method ="), True),
    ('service_type', _("Service Type ="), True),
)


class SegmentFilterAction(tables.FilterAction):
    filter_type = "server"
    filter_choices = SEGMENT_FILTER_CHOICES


class DeleteSegment(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Segment",
            u"Delete Segments",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Segment",
            u"Deleted Segments",
            count
        )

    def delete(self, request, segment_uuid):
        api.segment_delete(request, segment_uuid, ignore_missing=True)


class UpdateSegment(tables.LinkAction):
    name = "update"
    verbose_name = _("Update Segment")
    classes = ("ajax-modal",)

    def get_link_url(self, datum):
        obj_id = datum.uuid
        url = "horizon:masakaridashboard:segments:update"

        return reverse(url, args=[obj_id])


class FailoverSegmentTable(tables.DataTable):

    name = tables.WrappingColumn(
        'name', verbose_name=_("Name"),
        link="horizon:masakaridashboard:segments:detail", truncate=40)
    uuid = tables.Column('uuid', verbose_name=_("UUID"),
                         link="horizon:masakaridashboard:segments:detail")
    recovery_method = tables.Column(
        'recovery_method', verbose_name=_("Recovery Method"))
    service_type = tables.Column(
        'service_type', verbose_name=_("Service Type"))
    description = tables.WrappingColumn(
        'description', verbose_name=_("Description"),
        truncate=40)

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "failover_segment"
        verbose_name = _("FailoverSegment")
        table_actions = (DeleteSegment, CreateSegment, SegmentFilterAction)
        row_actions = (UpdateSegment,)
