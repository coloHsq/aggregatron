import django_tables2 as tables

from dcim.models import Rack, Device
from dcim.tables import DeviceTable, RackTable


class DeviceStatsTable(DeviceTable):
    ports_count = tables.Column(
        accessor='free_ports',
        verbose_name='Ports count',
        order_by='-free_ports'
    )

    actions = None

    class Meta(RackTable.Meta):
        model = Device
        fields = ('name', 'status', 'tenant', 'site', 'location', 'rack', 'role', 'manufacturer', 'device_type',
                  'ports_count')
        default_columns = fields

    def render_ports_count(self, value, record):
        return '{} / {}'.format(getattr(record, 'free_ports', '-'), getattr(record, 'ports', '-'))


class RackStatsTable(RackTable):
    rack = tables.Column(
        accessor='name',
        linkify=True
    )

    ports_count = tables.Column(
        accessor='free_ports',
        verbose_name='Ports count',
        order_by='-free_ports'
    )

    actions = None

    class Meta(RackTable.Meta):
        model = Rack
        fields = ('rack', 'role', 'tenant', 'ports_count')
        default_columns = fields

    def render_ports_count(self, value, record):
        return '{} / {}'.format(getattr(record, 'free_ports', '-'), getattr(record, 'ports', '-'))
