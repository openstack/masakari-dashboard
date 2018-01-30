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

import itertools

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon.utils import functions as utils
from horizon.utils import memoized
from keystoneauth1.identity.generic import token
from keystoneauth1 import session as ks_session
from openstack import connection

from masakaridashboard.handle_errors import handle_errors


@memoized.memoized
def openstack_connection(request):
    auth = token.Token(
        auth_url=getattr(settings, 'OPENSTACK_KEYSTONE_URL'),
        token=request.user.token.id,
        project_name=request.user.project_name,
        project_id=request.user.tenant_id)
    session = ks_session.Session(auth=auth)
    conn = connection.Connection(session=session)

    return conn.instance_ha


@handle_errors(_("Unable to retrieve segments"), [])
def get_segment_list(request, marker='', paginate=False, filters=None):
    """Returns segments as per page size."""
    page_size = utils.get_page_size(request)
    client = openstack_connection(request)
    kwargs = get_request_param(marker, paginate, filters, page_size)
    entities_iter = client.segments(**kwargs)
    has_prev_data = has_more_data = False
    if paginate:
        entities, has_more_data, has_prev_data = pagination_process(
            entities_iter, kwargs['limit'], page_size, marker)
    else:
        entities = list(entities_iter)

    return entities, has_more_data, has_prev_data


def get_request_param(marker, paginate, filters, page_size):
    limit = getattr(settings, 'API_RESULT_LIMIT', 100)

    if paginate:
        request_size = page_size + 1
    else:
        request_size = limit

    kwargs = {"marker": marker,
              "limit": request_size
              }
    if filters is not None:
        kwargs.update(filters)
    return kwargs


def pagination_process(data, request_size, page_size, marker):
    """Retrieve a listing of specific entity and handles pagination.

    :param request: Request data
    :param marker: Pagination marker for large data sets: entity id
    :param paginate: If true will perform pagination based on settings.
                     Default:False
    """
    prev_data = more_data = False
    entities = list(itertools.islice(data, request_size))
    # first and middle page condition
    if len(entities) > page_size:
        entities.pop()
        more_data = True
        # middle page condition
        if marker is not None:
            prev_data = True
    elif marker is not None:
        prev_data = True

    return entities, more_data, prev_data


@handle_errors(_("Unable to retrieve segments"), [])
def segment_list(request):
    return list(openstack_connection(request).segments())


def segment_create(request, data):
    """Create segment."""
    return openstack_connection(request).create_segment(**data)


@handle_errors(_("Unable to retrieve segment"), [])
def get_segment(request, segment_id):
    """Returns segment by id"""
    return openstack_connection(request).get_segment(segment_id)


@handle_errors(_("Unable to delete segment"), [])
def segment_delete(request, segment_id, ignore_missing=True):
    return openstack_connection(request).delete_segment(
        segment_id, ignore_missing)


@handle_errors(_("Unable to update segment"), [])
def segment_update(request, segment_id, fields_to_update):
    """Update segment."""
    return openstack_connection(request).update_segment(
        segment_id, **fields_to_update)
