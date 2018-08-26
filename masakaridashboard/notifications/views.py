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
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from masakaridashboard.api import api
from masakaridashboard.notifications import tables as notification_tab
from masakaridashboard.notifications import tabs as not_tab


class IndexView(tables.DataTableView):
    table_class = notification_tab.NotificationsTable
    template_name = 'masakaridashboard/notifications/index.html'
    page_title = _("Notifications")

    _more = False
    _prev = False

    def needs_filter_first(self, table):
        return self._needs_filter_first

    def has_more_data(self, table):
        return self._more

    def has_prev_data(self, table):
        return self._prev

    def get_data(self):
        notification_list = []

        marker = self.request.GET.get(
            notification_tab.NotificationsTable._meta.pagination_param,
            None
        )
        if marker is not None:
            try:
                notification = api.get_notification(self.request, marker)
                marker = notification.id
            except Exception:
                msg = _('Unable to get notification "%s".') % marker
                redirect = reverse(
                    'horizon:masakaridashboard:notifications:index')
                exceptions.handle(self.request, msg, redirect=redirect)

        filters = self.get_filters()
        self._needs_filter_first = True

        filter_first = getattr(settings, 'FILTER_DATA_FIRST', {})
        if filter_first.get('masakaridashboard.notifications', False) and len(
                filters) == 0:
            self._needs_filter_first = True
            self._more = False
            return notification_list
        try:
            notification_list, self._more, self._prev = api.notification_list(
                self.request, filters=filters, marker=marker, paginate=True)
        except Exception:
            self._prev = False
            self._more = False
            msg = _('Unable to retrieve notification list.')
            exceptions.handle(self.request, msg)
        return notification_list


class DetailView(tabs.TabbedTableView):
    tab_group_class = not_tab.NotificationDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ notification.notification_uuid }}"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        notification = self.get_data()
        table = notification_tab.NotificationsTable(self.request)
        context["notification"] = notification
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(notification)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            notification_id = self.kwargs['notification_id']
            notification = api.get_notification(self.request, notification_id)
        except Exception:
            msg = _('Unable to get notification "%s".') % notification_id
            redirect = reverse('horizon:masakaridashboard:notifications:index')
            exceptions.handle(self.request, msg, redirect=redirect)

        return notification

    def get_redirect_url(self):
        return reverse('horizon:masakaridashboard:notifications:index')

    def get_tabs(self, request, *args, **kwargs):
        notification = self.get_data()
        return self.tab_group_class(
            request, notification=notification, **kwargs)
