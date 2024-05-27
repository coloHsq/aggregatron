from netbox.plugins import PluginConfig


class AggregatronConfig(PluginConfig):
    """
    This class defines attributes for the NetBox Animal Sounds plugin.
    """
    # Plugin package name
    name = 'aggregatron'

    # Human-friendly name and description
    verbose_name = 'Aggregatron'

    # Plugin version
    version = '0.1'

    # Plugin author
    author = 'Davide Colombo'

    # Configuration parameters that MUST be defined by the user (if any)
    required_settings = []

    # Default configuration parameter values, if not set by the user
    default_settings = {}

    # Base URL path. If not set, the plugin name will be used.
    base_url = 'aggregatron'


config = AggregatronConfig
