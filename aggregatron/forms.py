from aggregatron.choices import PortTypeChoicesSubSet
from dcim.forms import DeviceFilterForm, RackFilterForm

__all__ = ('get_rack_stats_filter_form', 'get_device_stats_filter_form')

from utilities.forms.rendering import FieldSet

from utilities.forms.widgets import HTMXSelect

from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import DynamicModelChoiceField
from utilities.forms.widgets import NumberWithOptions


# region nested forms
class _NestedDeviceFilterForm(forms.Form):

    device_fieldsets = (FieldSet('n_device_type_id', 'n_device_role_id', name=_('Device')),)

    n_device_type_id = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label=_('Device type')
    )
    n_device_role_id = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label=_('Device role')
    )


class _InterfaceFilterForm(forms.Form):

    nested_fieldsets = (
        FieldSet('n_type', 'n_speed', 'n_duplex', 'n_enabled', 'n_mgmt_only', name=_('Attributes')),
        FieldSet('n_poe_mode', 'n_poe_type', name=_('PoE'))
    )

    n_type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=InterfaceTypeChoices,
        required=False
    )
    n_speed = forms.IntegerField(
        label=_('Speed'),
        required=False,
        widget=NumberWithOptions(
            options=InterfaceSpeedChoices
        )
    )
    n_duplex = forms.MultipleChoiceField(
        label=_('Duplex'),
        choices=InterfaceDuplexChoices,
        required=False
    )
    n_enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    n_mgmt_only = forms.NullBooleanField(
        label=_('Mgmt only'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    n_poe_mode = forms.MultipleChoiceField(
        choices=InterfacePoEModeChoices,
        required=False,
        label=_('PoE mode')
    )
    n_poe_type = forms.MultipleChoiceField(
        choices=InterfacePoETypeChoices,
        required=False,
        label=_('PoE type')
    )


class _FrontPortFilterForm(forms.Form):
    nested_fieldsets = (
        FieldSet('n_type',name=_('Attributes')),
    )
    n_type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=PortTypeChoices,
        required=False
    )


class _RearPortFilterForm(forms.Form):
    nested_fieldsets = (
        FieldSet('n_type', name=_('Attributes')),
    )
    n_type = forms.MultipleChoiceField(
        label=_('Type'),
        choices=PortTypeChoices,
        required=False
    )


# endregion


# region rack stats forms
class _RackStatsFilterForm(RackFilterForm):
    # field use to define the model used to run aggregations
    aggregate_on = forms.ChoiceField(
        choices=PortTypeChoicesSubSet,
        label='Port type',
        required=False,
        widget=HTMXSelect(hx_target_id='filter-fields')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fieldsets = self.fieldsets + (FieldSet('aggregate_on', name=_('Ports aggregation')),)


def custom_rack_init(cls, *args, **kwargs):
    super(type(cls), cls).__init__(*args, **kwargs)
    cls.fieldsets = cls.fieldsets + cls.nested_fieldsets + cls.device_fieldsets


def get_rack_stats_filter_form(aggregate_on):
    """
        hack to have dynamic subclasssing to import the needed fields depending on what
        type of "port" the filter is applied
    """
    if aggregate_on == 'interface':
        return type(
            'Rsf',
            (_RackStatsFilterForm, _InterfaceFilterForm, _NestedDeviceFilterForm),
            {'__init__': custom_rack_init}
        )
    if aggregate_on == 'frontport':
        return type(
            'Rsf',
            (_RackStatsFilterForm, _FrontPortFilterForm, _NestedDeviceFilterForm),
            {'__init__': custom_rack_init}
        )
    if aggregate_on == 'rearport':
        return type(
            'Rsf',
            (_RackStatsFilterForm, _RearPortFilterForm, _NestedDeviceFilterForm),
            {'__init__': custom_rack_init}
        )
    return _RackStatsFilterForm


# endregion


# region device stats forms
class _DeviceStatsFilterForm(DeviceFilterForm):
    # field use to define the model used to run aggregations
    aggregate_on = forms.ChoiceField(
        choices=PortTypeChoicesSubSet,
        label='Port type',
        required=False,
        widget=HTMXSelect(hx_target_id='filter-fields')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fieldsets = self.fieldsets + (FieldSet('aggregate_on', name=_('Ports aggregation')),)


def custom_device_init(cls, *args, **kwargs):
    super(type(cls), cls).__init__(*args, **kwargs)
    cls.fieldsets = cls.fieldsets + cls.nested_fieldsets


def get_device_stats_filter_form(aggregate_on):
    """
        hack to have dynamic subclasssing to import the needed fields depending on what
        type of "port" the filter is applied
    """
    if aggregate_on == 'interface':
        return type(
            'Dsf',
            (_DeviceStatsFilterForm, _InterfaceFilterForm),
            {'__init__': custom_device_init}
        )
    if aggregate_on == 'frontport':
        return type(
            'Dsf',
            (_DeviceStatsFilterForm, _FrontPortFilterForm),
            {'__init__': custom_device_init}
        )
    if aggregate_on == 'rearport':
        return type(
            'Dsf',
            (_DeviceStatsFilterForm, _RearPortFilterForm),
            {'__init__': custom_device_init}
        )
    return _DeviceStatsFilterForm
# endregion
