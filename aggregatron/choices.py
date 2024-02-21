from utilities.choices import ChoiceSet


class PortTypeChoicesSubSet(ChoiceSet):

    INTERFACE = 'interface'
    FRONT_PORT = 'frontport'
    REAR_PORT = 'rearport'

    CHOICES = (
        (None, '--------'),
        (INTERFACE, 'Interfaces'),
        (FRONT_PORT, 'Front Ports'),
        (REAR_PORT, 'Rear Ports')
    )
