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
import mock

from masakaridashboard.test import helpers as test


INDEX_URL = reverse('horizon:masakaridashboard:hosts:index')


class HostTest(test.TestCase):

    def test_index(self):
        hosts = self.masakari_host.list()
        segments = self.masakari_segment.list()
        with mock.patch('masakaridashboard.api.api.segment_list',
                        return_value=segments), mock.patch(
                'masakaridashboard.api.api.get_segment',
                return_value=segments[0]), mock.patch(
                'masakaridashboard.api.api.get_host_list',
                return_value=hosts):
            res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(res, 'masakaridashboard/hosts/index.html')

    def test_create_post(self):
        segment = self.masakari_segment.list()
        host = self.masakari_host.list()[0]
        hypervisors = self.hypervisors.list()
        create_url = reverse('horizon:masakaridashboard:segments:addhost',
                             args=[segment[0].uuid])
        form_data = {
            'segment_id': host.failover_segment_id,
            'segment_name': segment[0].name,
            'name': host.name,
            'type': host.type,
            'reserved': '1',
            'control_attributes': host.control_attributes,
            'on_maintenance': '0'
        }
        with mock.patch('masakaridashboard.api.api.segment_list',
                        return_value=segment), mock.patch(
                'masakaridashboard.api.api.get_host_list',
                return_value=[]), mock.patch(
                'masakaridashboard.api.api.get_hypervisor_list',
                return_value=hypervisors), mock.patch(
                'masakaridashboard.api.api.get_segment',
                return_value=segment[0]), mock.patch(
            'masakaridashboard.api.api.create_host',
                return_value=host) as mocked_create:
            res = self.client.post(create_url, form_data)
        self.assertNoFormErrors(res)
        self.assertEqual(res.status_code, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        mocked_create.assert_called_once_with(
            mock.ANY,
            form_data
        )
