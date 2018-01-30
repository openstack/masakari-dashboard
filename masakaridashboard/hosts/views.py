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

from django.conf import settings
from horizon import tables

from masakaridashboard.api import api
from masakaridashboard.hosts import tables as masakari_tab


class IndexView(tables.DataTableView):
    table_class = masakari_tab.HostTable
    template_name = 'masakaridashboard/hosts/index.html'

    def needs_filter_first(self, table):
        return self._needs_filter_first

    def get_data(self):
        segments = api.segment_list(self.request)
        host_list = []
        filters = self.get_filters()
        self._needs_filter_first = True

        filter_first = getattr(settings, 'FILTER_DATA_FIRST', {})
        if filter_first.get('masakaridashboard.hosts', False) and len(
                filters) == 0:
            self._needs_filter_first = True
            self._more = False
            return host_list

        for segment in segments:
            host_gen = api.get_host_list(self.request, segment.uuid, filters)
            for item in host_gen:
                host_list.append(item)

        return host_list
