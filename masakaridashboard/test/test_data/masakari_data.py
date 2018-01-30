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

from openstack.instance_ha.v1 import segment

from openstack_dashboard.test.test_data import utils as test_data_utils

from masakaridashboard.test import uuidsentinel


def data(TEST):
    TEST.masakari_segment = test_data_utils.TestDataContainer()

    segment1 = segment.Segment(uuid=uuidsentinel.segment1, name='test',
                               recovery_method='auto',
                               service_type='service', description='demo')
    segment2 = segment.Segment(uuid=uuidsentinel.segment2,
                               name='test2', recovery_method='auto',
                               service_type='service', description='demo')
    segment3 = segment.Segment(uuid=uuidsentinel.segment3, name='test3',
                               recovery_method='auto',
                               service_type='service', description='demo')

    TEST.masakari_segment.add(segment1)
    TEST.masakari_segment.add(segment2)
    TEST.masakari_segment.add(segment3)
