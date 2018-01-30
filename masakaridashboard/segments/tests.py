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

import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils.http import urlunquote
from openstack_dashboard.test import helpers

from masakaridashboard.segments import tables as segment_table
from masakaridashboard.test import helpers as test


INDEX_URL = reverse('horizon:masakaridashboard:segments:index')
CREATE_URL = reverse('horizon:masakaridashboard:segments:create_segment')


class SegmentTest(test.TestCase):

    def test_index(self):
        with mock.patch(
                'masakaridashboard.api.api.get_segment_list',
                return_value=[self.masakari_segment.list(),
                              False, False]) as mock_get_segment_list:
            res = self.client.get(INDEX_URL)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'masakaridashboard/segments/index.html')
        mock_get_segment_list.assert_called_once_with(
            filters={}, marker=None, paginate=True,
            request=helpers.IsHttpRequest())
        segments = res.context['failover_segment_table'].data
        self.assertItemsEqual(segments, self.masakari_segment.list())

    def test_create_get(self):
        res = self.client.get(CREATE_URL)
        self.assertTemplateUsed(res, 'masakaridashboard/segments/create.html')

    def test_create_post(self):
        segment = self.masakari_segment.list()[0]
        form_data = {
            'name': segment.name,
            'recovery_method': segment.recovery_method,
            'service_type': segment.service_type,
            'description': segment.description
        }
        with mock.patch('masakaridashboard.api.api.segment_create',
                        return_value=segment) as mocked_create:
            res = self.client.post(CREATE_URL, form_data)
        self.assertNoFormErrors(res)
        self.assertEqual(res.status_code, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)

        mocked_create.assert_called_once_with(
            helpers.IsHttpRequest(),
            form_data
        )

    def _test_segments_index_paginated(
            self, filters, marker, segments, url, has_more, has_prev):

        with mock.patch(
                'masakaridashboard.api.api.get_segment_list',
                return_value=[segments,
                              has_more, has_prev]) as mock_get_segment_list:
            res = self.client.get(urlunquote(url))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'masakaridashboard/segments/index.html')
        mock_get_segment_list.assert_called_once_with(
            filters=filters, marker=marker, paginate=True,
            request=helpers.IsHttpRequest())

        return res

    @override_settings(API_RESULT_PAGE_SIZE=1)
    @mock.patch('masakaridashboard.api.api.get_segment')
    def test_segments_index_paginated(self, mock_get_segment):
        mock_get_segment.return_value = self.masakari_segment.list()[0]
        segment_list = self.masakari_segment.list()
        size = settings.API_RESULT_PAGE_SIZE
        base_url = INDEX_URL
        next = segment_table.FailoverSegmentTable._meta.pagination_param

        # get first page
        expected_segments = segment_list[:size]
        res = self._test_segments_index_paginated(filters={}, marker=None,
                                                  segments=expected_segments,
                                                  url=base_url, has_more=True,
                                                  has_prev=False)
        segments = res.context['failover_segment_table'].data
        self.assertItemsEqual(segments, expected_segments)

        # get second page
        expected_segments = segment_list[size:2 * size]
        marker = expected_segments[0].id

        url = base_url + "?%s=%s" % (next, marker)
        res = self._test_segments_index_paginated(filters={}, marker=marker,
                                                  segments=expected_segments,
                                                  url=url, has_more=True,
                                                  has_prev=True)
        segments = res.context['failover_segment_table'].data
        self.assertItemsEqual(segments, expected_segments)

        # get last page
        expected_segments = segment_list[-size:]
        marker = expected_segments[0].id
        url = base_url + "?%s=%s" % (next, marker)
        res = self._test_segments_index_paginated(filters={}, marker=marker,
                                                  segments=expected_segments,
                                                  url=url, has_more=False,
                                                  has_prev=True)
        segments = res.context['failover_segment_table'].data
        self.assertItemsEqual(segments, expected_segments)

    @override_settings(API_RESULT_PAGE_SIZE=1)
    def test_segments_index_paginated_prev_page(self):
        segment_list = self.masakari_segment.list()
        size = settings.API_RESULT_PAGE_SIZE
        base_url = INDEX_URL
        prev = segment_table.FailoverSegmentTable._meta.prev_pagination_param

        # prev from some page
        expected_segments = segment_list[size:2 * size]
        marker = expected_segments[0].id
        url = base_url + "?%s=%s" % (prev, marker)
        res = self._test_segments_index_paginated(filters={}, marker=marker,
                                                  segments=expected_segments,
                                                  url=url, has_more=True,
                                                  has_prev=True)
        segments = res.context['failover_segment_table'].data
        self.assertItemsEqual(segments, expected_segments)

        # back to first page
        expected_segments = segment_list[:size]
        marker = expected_segments[0].id
        url = base_url + "?%s=%s" % (prev, marker)
        res = self._test_segments_index_paginated(
            filters={}, marker=marker, segments=expected_segments,
            url=url, has_more=True, has_prev=False)
        segments = res.context['failover_segment_table'].data
        self.assertItemsEqual(segments, expected_segments)

    def test_delete_ok(self):

        segment = self.masakari_segment.list()[0]
        data = {'object_ids': [segment.uuid],
                'action': 'failover_segment__delete'}
        with mock.patch(
                'masakaridashboard.api.api.get_segment_list',
                return_value=(self.masakari_segment.list(), True, True)
        ), mock.patch(
                'masakaridashboard.api.api.segment_delete',
                return_value=None
        ) as mocked_delete:
            res = self.client.post(INDEX_URL, data)

        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        mocked_delete.assert_called_once_with(
            helpers.IsHttpRequest(),
            segment.uuid,
            ignore_missing=True
        )

    def test_detail(self):
        segment = self.masakari_segment.list()[0]
        detail_url = reverse('horizon:masakaridashboard:segments:detail',
                             args=[segment.uuid])
        with mock.patch('masakaridashboard.api.api.get_segment',
                        return_value=segment):
            res = self.client.get(detail_url)
        self.assertNoFormErrors(res)
        self.assertEqual(200, res.status_code)
        self.assertEqual(segment.uuid, res.context['segment'].uuid)
        self.assertTemplateUsed(res, 'horizon/common/_detail.html')
        self.assertTemplateUsed(
            res, 'masakaridashboard/segments/_detail_overview.html')

    def test_update(self):
        segment_obj = self.masakari_segment.list()[0]
        update_url = reverse('horizon:masakaridashboard:segments:update',
                             args=[segment_obj.uuid])
        segment_obj.name = 'fake'
        form_data = {
            'uuid': segment_obj.uuid,
            'name': segment_obj.name,
            'recovery_method': segment_obj.recovery_method,
            'description': segment_obj.description}

        with mock.patch(
                'masakaridashboard.api.api.get_segment',
                return_value=self.masakari_segment.list()[0]), mock.patch(
            'masakaridashboard.api.api.segment_update',
                return_value=segment_obj) as mocked_update:
            res = self.client.post(update_url, form_data)
        self.assertNoFormErrors(res)
        self.assertEqual(res.status_code, 302)
        self.assertRedirectsNoFollow(res, INDEX_URL)
        data_to_update = {
            'name': segment_obj.name,
            'recovery_method': segment_obj.recovery_method,
            'description': segment_obj.description}

        mocked_update.assert_called_once_with(
            helpers.IsHttpRequest(),
            segment_obj.uuid,
            data_to_update
        )
