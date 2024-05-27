from netbox.plugins import PluginMenuItem

menu_items = (

    PluginMenuItem(
        link='plugins:aggregatron:rack_list',
        link_text='Rack ports overview',
        permissions=['dcim.view_rack', 'dcim.view_interface', 'dcim.view_frontport', 'dcim.view_rearport'],
    ),

    PluginMenuItem(
        link='plugins:aggregatron:device_list',
        link_text='Device ports overview',
        permissions=['dcim.view_rack', 'dcim.view_interface', 'dcim.view_frontport', 'dcim.view_rearport'],
    )
)
