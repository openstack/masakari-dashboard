# Copyright (c) 2018 NTT DATA
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

from django.utils.translation import ugettext_lazy as _

from horizon import tabs

from masakaridashboard.api import api
from masakaridashboard.hosts import tables as host_table


class OverviewTab(tabs.Tab):
    name = _("Segment")
    slug = "segment"
    template_name = ("masakaridashboard/segments/_detail_overview.html")

    def get_context_data(self, request):
        return {"segment": self.tab_group.kwargs['segment']}


class HostTab(tabs.TableTab):
    table_classes = (host_table.HostTable,)
    name = _("Hosts")
    slug = "host_tab"
    template_name = "horizon/common/_detail_table.html"
    preload = False

    def get_host_data(self):
        segment_data = self.tab_group.kwargs['segment_id']
        if len(segment_data.split(',')) > 1:
            segment_id = segment_data.split(',')[1]
        else:
            segment_id = segment_data

        host_list = []

        host_gen = api.get_host_list(self.request, segment_id, filters={})

        for item in host_gen:
            host_list.append(item)

        return host_list


class SegmentDetailTabs(tabs.DetailTabsGroup):
    slug = "segment_details"
    tabs = (OverviewTab, HostTab)
