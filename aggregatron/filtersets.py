import django_filters
from django.contrib.contenttypes.models import ContentType
from django.db.models import OuterRef, Count, Subquery, Q
from django.db.models.functions import Coalesce
from django.utils.module_loading import import_string

from dcim.filtersets import RackFilterSet, DeviceFilterSet

__all__ = ('RackStatsFilterSet', 'DeviceStatsFilterSet')


class DynFilterSet(django_filters.FilterSet):
    subquery_key = None

    aggregate_on = django_filters.CharFilter(
        method='_aggregate_on',
        label='Port Type'
    )

    def _dyn_model_selector(self, model_name):
        """
            dynamically resolve models base on filter form selection
        """
        try:
            ct = ContentType.objects.get(app_label='dcim', model=model_name).model_class()
        except ContentType.DoesNotExist:
            ct = None
        return ct

    def _aggregate_on(self, queryset, name, value):
        """
            based on the model returned by _dyn_model_selector(),
            replaces the empty annotation on view's queryset with the one created here
        """
        model = self._dyn_model_selector(value)
        if model is None:
            return queryset
        aggregation_filters = {key.lstrip('n_'): [value] for key, value in self.data.items() if key.startswith('n_')}
        dyn_filterset = import_string(f'dcim.filtersets.{model._meta.object_name}FilterSet')
        base_qs = dyn_filterset(data=aggregation_filters, queryset=model.objects.all()).qs
        ports = base_qs.filter(Q((self.subquery_key, OuterRef('pk'))))
        total = ports.order_by().values(self.subquery_key).annotate(count=Count('pk')).values('count')
        free = ports.filter(cable__isnull=True, mark_connected=False).order_by().values(self.subquery_key).annotate(
            count=Count('pk')).values('count')
        return queryset.annotate(ports=Coalesce(Subquery(total), 0)).annotate(
            free_ports=Coalesce(Subquery(free), 0)).filter(
            ports__gte=1
        )


class RackStatsFilterSet(RackFilterSet, DynFilterSet):
    subquery_key = 'device__rack'

    class Meta(RackFilterSet.Meta):
        def __init__(self):
            super().__init__()
            self.fields = self.fields + ['aggregate_on']


class DeviceStatsFilterSet(DeviceFilterSet, DynFilterSet):
    subquery_key = 'device'

    class Meta(DeviceFilterSet.Meta):
        def __init__(self):
            super().__init__()
            self.fields = self.fields + ['aggregate_on']
