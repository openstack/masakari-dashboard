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

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from masakaridashboard.api import api
from masakaridashboard.segments import tables as masakari_tab

from horizon import exceptions
from horizon import forms

from horizon.utils import memoized
from masakaridashboard.segments import forms as segment_forms

from horizon import tabs
from masakaridashboard.segments import tabs as seg_tab


class IndexView(tables.DataTableView):
    table_class = masakari_tab.FailoverSegmentTable
    template_name = 'masakaridashboard/segments/index.html'
    page_title = _("Segments")

    _more = False
    _prev = False

    def needs_filter_first(self, table):
        return self._needs_filter_first

    def has_more_data(self, table):
        return self._more

    def has_prev_data(self, table):
        return self._prev

    def get_data(self):
        segments = []
        marker = self.request.GET.get(
            masakari_tab.FailoverSegmentTable._meta.pagination_param,
            None
        )
        if marker is not None:
            segment = api.get_segment(self.request, marker)
            marker = segment.id
        filters = self.get_filters()
        self._needs_filter_first = True

        filter_first = getattr(settings, 'FILTER_DATA_FIRST', {})
        if filter_first.get('masakaridashboard.segments', False) and len(
                filters) == 0:
            self._needs_filter_first = True
            self._more = False
            return segments

        try:
            segments, self._more, self._prev = api.get_segment_list(
                request=self.request,
                marker=marker,
                filters=filters,
                paginate=True
            )
        except Exception:
            self._prev = False
            self._more = False
            msg = _('Unable to retrieve segment list.')
            exceptions.handle(self.request, msg)

        return segments


class CreateSegmentView(forms.ModalFormView):
    template_name = 'masakaridashboard/segments/create.html'
    modal_header = _("Create Segment")
    form_id = "create_segment"
    form_class = segment_forms.CreateSegmentForm
    submit_label = _("Create")
    submit_url = reverse_lazy(
        "horizon:masakaridashboard:segments:create_segment")
    success_url = reverse_lazy("horizon:masakaridashboard:segments:index")
    page_title = _("Create Segment")

    def get_form_kwargs(self):
        kwargs = super(CreateSegmentView, self).get_form_kwargs()
        return kwargs


class DetailView(tabs.TabbedTableView):
    tab_group_class = seg_tab.SegmentDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ segment.name|default:segment.id }}"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        segment = self.get_data()
        table = masakari_tab.FailoverSegmentTable(self.request)
        context["segment"] = segment
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(segment)
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            segment_id = self.kwargs['segment_id']
            segment = api.get_segment(self.request, segment_id)
        except Exception:
            msg = _('Unable to get segment "%s".') % segment_id
            redirect = reverse('horizon:masakaridashboard:segments:index')
            exceptions.handle(self.request, msg, redirect=redirect)

        return segment

    def get_redirect_url(self):
        return reverse('horizon:masakaridashboard:segments:index')

    def get_tabs(self, request, *args, **kwargs):
        segment = self.get_data()
        return self.tab_group_class(request, segment=segment, **kwargs)


class UpdateView(forms.ModalFormView):
    template_name = 'masakaridashboard/segments/update.html'
    modal_header = _("Update Segment")
    form_id = "update_segment"
    form_class = segment_forms.UpdateForm
    submit_label = _("Update")
    submit_url = "horizon:masakaridashboard:segments:update"
    success_url = reverse_lazy("horizon:masakaridashboard:segments:index")
    page_title = _("Update Segment")

    @memoized.memoized_method
    def get_object(self):
        try:
            segment = api.get_segment(self.request, self.kwargs['segment_id'])
            return segment
        except Exception:
            msg = _('Unable to retrieve segment.')
            redirect = reverse('horizon:masakaridashboard:segments:index')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['submit_url'] = reverse(
            self.submit_url,
            args=[self.kwargs["segment_id"]]
        )

        return context

    def get_initial(self, **kwargs):
        segment = self.get_object()

        return {'uuid': self.kwargs['segment_id'],
                'name': segment.name,
                'recovery_method': segment.recovery_method,
                'description': segment.description}
