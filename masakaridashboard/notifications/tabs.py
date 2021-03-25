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

from horizon import exceptions
from horizon import tabs

from masakaridashboard.api import api
from masakaridashboard.notifications import tables as notification_tab


class OverviewTab(tabs.Tab):
    name = _("Notifications")
    slug = "notifications"
    template_name = ("masakaridashboard/notifications/_detail_overview.html")

    def get_context_data(self, request):
        return {"notification": self.tab_group.kwargs['notification']}


class NotificationProgressDetailsTab(tabs.TableTab):
    table_classes = (notification_tab.NotificationProgressDetailsTable,)
    name = _("Progress Details")
    slug = "notification_progress_details"
    template_name = "masakaridashboard/notifications/_progress_detail.html"
    preload = False

    def get_notification_progress_details_data(self):
        try:
            id = 0
            notification = self.tab_group.kwargs['notification']
            notification_obj = \
                api.get_notification_with_progress_details(
                    self.request, notification.notification_uuid)
            progress_detail_list = []
            for progress_detail in notification_obj.recovery_workflow_details:
                # Retrieve progress name from detailed name.
                action = progress_detail['name']
                for task in progress_detail['progress_details']:
                    id = id + 1
                    progress_obj = notification_tab.ProgressDetailsItem(
                        id,
                        action,
                        task['timestamp'],
                        task['message']
                    )
                    progress_detail_list.append(progress_obj)
            return progress_detail_list
        except Exception:
            error_message = (_("Failed to get progress details for "
                               "notification '%s'.")
                             % notification.notification_uuid)
            exceptions.handle(self.request, error_message)
            return []


class NotificationDetailTabs(tabs.DetailTabsGroup):
    slug = "notification_details"
    tabs = (OverviewTab, NotificationProgressDetailsTab)
