# Netbox dynamic ports count

This plugin aims to give an overview of ports availability at both rack and device level.  
Basically it's just a clone of standards racks and devices view, with an added column for ports count (free/total)  

![Screenshot 2024-02-20 alle 17 51 18](https://github.com/coloHsq/aggregatron/assets/46020242/6e86c786-f4e1-4fa8-a8a5-496894d2750d)
*This can be explained as: given a location, show the port count for all racks that contains a switch with at least one free 40GE port*

All the "magic" is done with dynamic count subqueries, driven by a custom form that extends the base ones (devices and racks) by adding the various ports types filtering options.

![Screenshot 2024-02-20 alle 17 52 03](https://github.com/coloHsq/aggregatron/assets/46020242/70c95afa-f63c-47bc-8eba-18f41b1fe266)
*For instance, the "ports aggregation" field is always threre, the other fields are dynamically added based on its selection*

By now, "free ports" are counted with the same condition of stock Netbox's filter "Occupied == No", meaning no cable connected and not marked as connected.


## Installing
If you have already installed some other plugin, just repeat the process and everything should be just fine.  
If it's the first time installing a plugin, follow this steps:  
1. Clone this repo into a "convenient" directory to be used in Netbox. (e.g. a "plugin" directory inside netbox root)
2. Add `'aggregatron'` to `PLUGINS` in Netbox's `configuration.py`
3. Create `local_requirements.txt` in Netbox root directory and add `-e /path/to/plugin/dir/`, this is needed to ensure the plugin gets re-intsalled with every Netbox update.
4. Install the plugin with `pip install -e path/to/plugin/dir/`, or just run `upgrade.sh`.
5. Restart Netbox services (`sudo systemctl restart netbox netbox-rq`)
6. Everything should be up n'running, and the entry points for racks and devices overview view should be available in the side menu.
