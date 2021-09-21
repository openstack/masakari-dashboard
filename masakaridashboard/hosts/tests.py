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

from unittest import mock

from django.urls import reverse

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
        self.assertEqual(res.status_code, 200)

    def test_create_post(self):
        segment = self.masakari_segment.list()
        host = self.masakari_host.list()[0]
        compute_services = self.compute_services.list()
        create_url = reverse('horizon:masakaridashboard:segments:addhost',
                             args=[segment[0].uuid])
        form_data = {
            'segment_id': host.failover_segment_id,
            'segment_name': segment[0].name,
            'name': host.name,
            'type': host.type,
            'reserved': host.reserved,
            'control_attributes': host.control_attributes,
            'on_maintenance': host.on_maintenance
        }
        with mock.patch('masakaridashboard.api.api.segment_list',
                        return_value=segment), mock.patch(
                'masakaridashboard.api.api.get_host_list',
                return_value=[]), mock.patch(
                'masakaridashboard.api.api.get_compute_service_list',
                return_value=compute_services), mock.patch(
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

    def test_delete_ok(self):
        host = self.masakari_host.list()[0]
        data = {'object_ids': host.uuid + ',' + host.failover_segment_id,
                'action': 'host__delete'}
        with mock.patch(
                'masakaridashboard.api.api.segment_list',
                return_value=[self.masakari_segment.first(
                )]), mock.patch(
                'masakaridashboard.api.api.get_host_list',
                return_value=self.masakari_host.list()), mock.patch(
                'masakaridashboard.api.api.delete_host',
                return_value=None
        ) as mocked_delete:
            res = self.client.post(INDEX_URL, data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        mocked_delete.assert_called_once_with(
            mock.ANY,
            host.uuid,
            host.failover_segment_id,
        )

    def test_detail(self):
        host = self.masakari_host.list()[0]
        id_to_update = host.uuid + ',' + host.failover_segment_id
        detail_url = reverse('horizon:masakaridashboard:hosts:detail',
                             args=[id_to_update])
        with mock.patch('masakaridashboard.api.api.get_host',
                        return_value=self.masakari_host.list()[0]):
            res = self.client.get(detail_url)
        self.assertNoFormErrors(res)
        self.assertEqual(200, res.status_code)
        self.assertTemplateUsed(res, 'horizon/common/_detail.html')
        self.assertTemplateUsed(
            res, 'masakaridashboard/hosts/_detail_overview.html')

    def test_update(self):
        host_to_update = self.masakari_host.list()[0]
        id_to_update = (
            host_to_update.uuid + ',' + host_to_update.failover_segment_id)
        update_url = reverse('horizon:masakaridashboard:hosts:update',
                             args=[id_to_update])
        host_to_update.control_attributes = 'fake'
        form_data = {
            'failover_segment_id': host_to_update.failover_segment_id,
            'uuid': host_to_update.uuid,
            'name': host_to_update.name,
            'type': host_to_update.type,
            'reserved': host_to_update.reserved,
            'control_attributes': host_to_update.control_attributes,
            'on_maintenance': host_to_update.on_maintenance
        }
        with mock.patch(
                'masakaridashboard.api.api.get_host',
                return_value=self.masakari_host.list()[0]), mock.patch(
                'masakaridashboard.api.api.update_host',
                return_value=host_to_update) as mocked_update:
            res = self.client.post(update_url, form_data)

        self.assertNoFormErrors(res)
        self.assertEqual(res.status_code, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        fields_to_update = {
            'name': host_to_update.name,
            'type': host_to_update.type,
            'reserved': host_to_update.reserved,
            'control_attributes': host_to_update.control_attributes,
            'on_maintenance': host_to_update.on_maintenance
        }

        mocked_update.assert_called_once_with(
            mock.ANY,
            host_to_update.uuid,
            host_to_update.failover_segment_id,
            fields_to_update
        )
