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

from unittest import mock

from django.conf import settings
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.http import urlunquote

from masakaridashboard.notifications import tables as notification_tab
from masakaridashboard.test import helpers as test

INDEX_URL = reverse('horizon:masakaridashboard:notifications:index')


class NotificationTest(test.TestCase):

    def test_index(self):
        notifications = self.masakari_notification.list()
        with mock.patch(
                'masakaridashboard.api.api.notification_list',
                return_value=[
                    notifications, False, False]) as mock_notification_list:
            res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(res,
                                'masakaridashboard/notifications/index.html')
        notifications_from_res = res.context['notifications_table'].data
        self.assertCountEqual(notifications_from_res, notifications)
        self.assertEqual(res.status_code, 200)
        mock_notification_list.assert_called_once_with(
            mock.ANY, filters={}, marker=None, paginate=True)

    def _test_notifications_index_paginated(
            self, filters, marker, notifications, url, has_more, has_prev):

        with mock.patch(
                'masakaridashboard.api.api.notification_list',
                return_value=[notifications,
                              has_more, has_prev]) as mock_notification_list:
            res = self.client.get(urlunquote(url))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res,
                                'masakaridashboard/notifications/index.html')
        mock_notification_list.assert_called_once_with(
            mock.ANY, filters=filters, marker=marker, paginate=True)

        return res

    @override_settings(API_RESULT_PAGE_SIZE=1)
    @mock.patch('masakaridashboard.api.api.get_notification')
    def test_notifications_index_paginated(self, mock_get_notification):
        get_single_notification = self.masakari_notification.list()[0]
        mock_get_notification.return_value = get_single_notification
        notification_list = self.masakari_notification.list()
        size = settings.API_RESULT_PAGE_SIZE
        base_url = INDEX_URL
        next = notification_tab.NotificationsTable._meta.pagination_param

        # get first page
        expected_notifications = notification_list[:size]
        res = self._test_notifications_index_paginated(
            filters={}, marker=None, notifications=expected_notifications,
            url=base_url, has_more=True, has_prev=False)
        notifications = res.context['notifications_table'].data
        self.assertCountEqual(notifications, expected_notifications)

        # get second page
        expected_notifications = notification_list[size:2 * size]
        marker = expected_notifications[0].id

        url = base_url + "?%s=%s" % (next, marker)
        res = self._test_notifications_index_paginated(
            filters={}, marker=marker, notifications=expected_notifications,
            url=url, has_more=True, has_prev=True)
        notifications = res.context['notifications_table'].data
        self.assertCountEqual(notifications, expected_notifications)

        # get last page
        expected_notifications = notification_list[-size:]
        marker = expected_notifications[0].id
        url = base_url + "?%s=%s" % (next, marker)
        res = self._test_notifications_index_paginated(
            filters={}, marker=marker, notifications=expected_notifications,
            url=url, has_more=False, has_prev=True)
        notifications = res.context['notifications_table'].data
        self.assertCountEqual(notifications, expected_notifications)

    @override_settings(API_RESULT_PAGE_SIZE=1)
    def test_notifications_index_paginated_prev_page(self):
        notification_list = self.masakari_notification.list()
        size = settings.API_RESULT_PAGE_SIZE
        base_url = INDEX_URL
        prev = notification_tab.NotificationsTable._meta.prev_pagination_param

        # prev from some page
        expected_notifications = notification_list[size:2 * size]
        marker = expected_notifications[0].id
        url = base_url + "?%s=%s" % (prev, marker)
        res = self._test_notifications_index_paginated(
            filters={}, marker=marker, notifications=expected_notifications,
            url=url, has_more=True, has_prev=True)
        notifications = res.context['notifications_table'].data
        self.assertCountEqual(notifications, expected_notifications)

        # back to first page
        expected_notifications = notification_list[:size]
        marker = expected_notifications[0].id
        url = base_url + "?%s=%s" % (prev, marker)
        res = self._test_notifications_index_paginated(
            filters={}, marker=marker, notifications=expected_notifications,
            url=url, has_more=True, has_prev=False)
        notifications = res.context['notifications_table'].data
        self.assertCountEqual(notifications, expected_notifications)
