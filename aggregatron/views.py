from django.db.models import Value, IntegerField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from core.models import ObjectType
from extras.models import ExportTemplate
from netbox.views.generic import ObjectListView
from netbox.views.generic.mixins import TableMixin
from netbox.views.generic.utils import get_prerequisite_model
from utilities.htmx import htmx_partial
from .filtersets import RackStatsFilterSet, DeviceStatsFilterSet
from .forms import get_rack_stats_filter_form, get_device_stats_filter_form
from .tables import *


class DynAggregationObjectListView(ObjectListView, TableMixin):
    actions = {'export': set()}
    additional_permissions = ('dcim.view_interface', 'dcim.view_fronport', 'dcim.view_rearport')

    def get_filterset_form(self, request):
        pass

    def get(self, request):
        """
        GET request handler.

        Args:
            request: The current request
        """
        model = self.queryset.model
        content_type = ObjectType.objects.get_for_model(model)

        if self.filterset:
            self.queryset = self.filterset(request.GET, self.queryset, request=request).qs

        # Determine the available actions
        actions = self.get_permitted_actions(request.user)
        has_bulk_actions = any([a.startswith('bulk_') for a in actions])

        if 'export' in request.GET:

            # Export the current table view
            if request.GET['export'] == 'table':
                table = self.get_table(self.queryset, request, has_bulk_actions)
                columns = [name for name, _ in table.selected_columns]
                return self.export_table(table, columns)

            # Render an ExportTemplate
            elif request.GET['export']:
                template = get_object_or_404(ExportTemplate, content_types=content_type, name=request.GET['export'])
                return self.export_template(template, request)

            # Check for YAML export support on the model
            elif hasattr(model, 'to_yaml'):
                response = HttpResponse(self.export_yaml(), content_type='text/yaml')
                filename = 'netbox_{}.yaml'.format(self.queryset.model._meta.verbose_name_plural)
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
                return response

            # Fall back to default table/YAML export
            else:
                table = self.get_table(self.queryset, request, has_bulk_actions)
                return self.export_table(table)

        # Render the objects table
        table = self.get_table(self.queryset, request, has_bulk_actions)

        # If this is an HTMX request, return only the rendered table HTML
        if htmx_partial(request):
            if request.headers.get('hx-target', None) == 'object_list':
                if request.GET.get('embedded', False):
                    table.embedded = True
                    # Hide selection checkboxes
                    if 'pk' in table.base_columns:
                        table.columns.hide('pk')
                return render(request, 'htmx/table.html', {
                    'table': table,
                })
            if request.headers.get('hx-target', None) == 'filter-fields':
                filter_form = self.get_filterset_form(request)
                return render(request, 'aggregatron/htmx/filter_form.html', {
                    'filter_form': filter_form,
                })

        context = {
            'model': model,
            'table': table,
            'actions': actions,
            'filter_form': self.get_filterset_form(request),
            'prerequisite_model': get_prerequisite_model(self.queryset),
            **self.get_extra_context(request),
        }

        return render(request, self.template_name, context)


class DeviceOverviewListView(DynAggregationObjectListView):
    filterset = DeviceStatsFilterSet
    table = DeviceStatsTable
    template_name = 'aggregatron/device_ports_overview_list.html'

    # Empty annotation needed to avoid field errors in table display,
    # probably there's a better way to accomplish this
    queryset = Device.objects.annotate(free_ports=Value(None, IntegerField(null=True)))

    def get_filterset_form(self, request):
        aggregate_on = request.GET.get('aggregate_on', None)
        return get_device_stats_filter_form(aggregate_on)(request.GET)


class RackOverviewListView(DynAggregationObjectListView):
    filterset = RackStatsFilterSet
    table = RackStatsTable
    template_name = 'aggregatron/rack_ports_overview_list.html'
    # Empty annotation needed to avoid field errors in table display,
    # probably there's a better way to accomplish this
    queryset = Rack.objects.annotate(free_ports=Value(None, IntegerField(null=True)))

    def get_filterset_form(self, request):
        aggregate_on = request.GET.get('aggregate_on', None)
        return get_rack_stats_filter_form(aggregate_on)(request.GET)
