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

from unittest import mock

from django.urls import reverse

from masakaridashboard.test import helpers as test

INDEX_URL = reverse('horizon:masakaridashboard:vmoves:index')


class VMoveTest(test.TestCase):

    def test_index(self):
        vmoves = self.masakari_vmove.list()
        notifications = self.masakari_notification.list()
        with mock.patch('masakaridashboard.api.api.get_notification_list',
                        return_value=notifications), mock.patch(
                'masakaridashboard.api.api.get_notification',
                return_value=notifications[0]), mock.patch(
                'masakaridashboard.api.api.get_vmoves_list',
                return_value=vmoves):
            res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(res, 'masakaridashboard/vmoves/index.html')
        self.assertEqual(res.status_code, 200)

    def test_detail(self):
        vmove = self.masakari_vmove.list()[0]
        id_to_update = vmove.uuid + ',' + vmove.notification_id
        detail_url = reverse('horizon:masakaridashboard:vmoves:detail',
                             args=[id_to_update])
        with mock.patch('masakaridashboard.api.api.get_vmove',
                        return_value=self.masakari_vmove.list()[0]):
            res = self.client.get(detail_url)
        self.assertNoFormErrors(res)
        self.assertEqual(200, res.status_code)
        self.assertTemplateUsed(res, 'horizon/common/_detail.html')
        self.assertTemplateUsed(
            res, 'masakaridashboard/vmoves/_detail_overview.html')
