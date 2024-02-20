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

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from masakaridashboard.api import api
from masakaridashboard.vmoves import tables as masakari_tab
from masakaridashboard.vmoves import tabs as vmove_tab


class IndexView(tables.DataTableView):
    table_class = masakari_tab.VMoveTable
    template_name = 'masakaridashboard/vmoves/index.html'
    page_title = _("VMoves")

    def needs_filter_first(self, table):
        return self._needs_filter_first

    def get_data(self):
        notifications = api.get_notification_list(self.request)
        vmove_list = []
        filters = self.get_filters()
        self._needs_filter_first = True

        filter_first = getattr(settings, 'FILTER_DATA_FIRST', {})
        if filter_first.get('masakaridashboard.vmoves', False) and len(
                filters) == 0:
            self._needs_filter_first = True
            self._more = False
            return vmove_list

        for notification in notifications:
            if notification.type != "COMPUTE_HOST":
                continue
            vmove_gen = api.get_vmoves_list(
                self.request, notification.notification_uuid, filters)
            for item in vmove_gen:
                vmove_list.append(item)

        return vmove_list


class DetailView(tabs.TabbedTableView):
    tab_group_class = vmove_tab.VMoveDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ vmove.server_name|default:vmove.server_name }}"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        vmove = self.get_data()
        table = masakari_tab.VMoveTable(self.request)
        context["vmove"] = vmove
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(vmove)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            row_data = self.kwargs['vmove_id'].split(',')
            notification_id = row_data[1]
            vmove_id = row_data[0]
            vmove = api.get_vmove(self.request, vmove_id, notification_id)
        except Exception:
            msg = _('Unable to get vmove "%s".') % vmove_id
            redirect = reverse('horizon:masakaridashboard:vmoves:index')
            exceptions.handle(self.request, msg, redirect=redirect)

        return vmove

    def get_redirect_url(self):
        return reverse('horizon:masakaridashboard:vmoves:index')

    def get_tabs(self, request, *args, **kwargs):
        vmove = self.get_data()
        return self.tab_group_class(request, vmove=vmove, **kwargs)
