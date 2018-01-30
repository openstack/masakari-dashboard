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
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from masakaridashboard.api import api
from masakaridashboard.hosts import tables as masakari_tab
from masakaridashboard.hosts import tabs as host_tab


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


class DetailView(tabs.TabbedTableView):
    tab_group_class = host_tab.HostDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ host.name|default:host.id }}"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        host = self.get_data()
        table = masakari_tab.HostTable(self.request)
        context["host"] = host
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(host)
        return context

    @memoized.memoized_method
    def get_data(self):
        row_data = self.kwargs['host_id'].split(',')
        segment_id = row_data[1]
        host_id = row_data[0]
        try:
            host = api.get_host(self.request, segment_id, host_id)
        except Exception:
            msg = _('Unable to get host "%s".') % host_id
            redirect = reverse('horizon:masakaridashboard:hosts:index')
            exceptions.handle(self.request, msg, redirect=redirect)

        return host

    def get_redirect_url(self):
        return reverse('horizon:masakaridashboard:hosts:index')

    def get_tabs(self, request, *args, **kwargs):
        host = self.get_data()
        return self.tab_group_class(request, host=host, **kwargs)
