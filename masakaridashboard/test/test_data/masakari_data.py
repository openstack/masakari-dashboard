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

import datetime
from oslo_utils import timeutils

from openstack.instance_ha.v1 import host
from openstack.instance_ha.v1 import notification
from openstack.instance_ha.v1 import segment
from openstack.instance_ha.v1 import vmove
from openstack_dashboard.test.test_data import utils as test_data_utils

from masakaridashboard.test import uuidsentinel
from novaclient.v2.services import Service
from novaclient.v2.services import ServiceManager

NOW = timeutils.utcnow().replace(microsecond=0)


def data(TEST):

    TEST.masakari_segment = test_data_utils.TestDataContainer()

    segment1 = segment.Segment(
        uuid=uuidsentinel.segment1,
        name='test',
        recovery_method='auto',
        service_type='service',
        description='demo',
        is_enabled=True,
    )
    segment2 = segment.Segment(
        uuid=uuidsentinel.segment2,
        name='test2',
        recovery_method='auto',
        service_type='service',
        description='demo',
        is_enabled=False,
    )
    segment3 = segment.Segment(
        uuid=uuidsentinel.segment3,
        name='test3',
        recovery_method='auto',
        service_type='service',
        description='demo',
        is_enabled=True,
    )

    TEST.masakari_segment.add(segment1)
    TEST.masakari_segment.add(segment2)
    TEST.masakari_segment.add(segment3)

    TEST.masakari_host = test_data_utils.TestDataContainer()

    host1 = host.Host(uuid=uuidsentinel.host1, name="test",
                      reserved='True', type='service',
                      control_attributes='test',
                      failover_segment_id=uuidsentinel.segment1,
                      on_maintenance='False')

    TEST.masakari_host.add(host1)

    TEST.compute_services = test_data_utils.TestDataContainer()

    service1 = Service(
        ServiceManager, {
            "id": 1, "host": "test",
        }
    )

    TEST.compute_services.add(service1)

    TEST.masakari_notification = test_data_utils.TestDataContainer()
    notification1 = notification.Notification(
        notification_uuid=uuidsentinel.notification1, status='new',
        generated_time=(NOW - datetime.timedelta(seconds=2)),
        payload='test', type='type1', source_host_uuid=uuidsentinel.host1)
    notification2 = notification.Notification(
        notification_uuid=uuidsentinel.notification2, status='running',
        generated_time=(NOW - datetime.timedelta(seconds=3)),
        payload='test', type='type2', source_host_uuid=uuidsentinel.host2)
    notification3 = notification.Notification(
        notification_uuid=uuidsentinel.notification3, status='error',
        generated_time=(NOW - datetime.timedelta(seconds=4)),
        payload='test', type='type3', source_host_uuid=uuidsentinel.host3)
    TEST.masakari_notification.add(notification1)
    TEST.masakari_notification.add(notification2)
    TEST.masakari_notification.add(notification3)
    TEST.masakari_vmove = test_data_utils.TestDataContainer()

    vmove1 = vmove.VMove(
        uuid=uuidsentinel.vmove1,
        notification_id=uuidsentinel.notification1,
        server_id=uuidsentinel.server1,
        server_name="vm",
        source_host='host1',
        dest_host='host2',
        start_time=(NOW - datetime.timedelta(seconds=3)),
        end_time=(NOW - datetime.timedelta(seconds=1)),
        status='succeeded',
        type='evacuation')

    TEST.masakari_vmove.add(vmove1)
