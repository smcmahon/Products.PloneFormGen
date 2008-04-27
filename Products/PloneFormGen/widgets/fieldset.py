"""Fieldset -- widgets for fieldset start / end"""

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget

class FieldsetStartWidget(TypesWidget):
    """
        This pseudo widget opens an XHTML fieldset.
    """

    _properties = TypesWidget._properties.copy()
    _properties.update({'macro' : 'widget_fieldset_start',
                        'show_legend' : True,
                        },)

# Register the widget with Archetypes
registerWidget(FieldsetStartWidget,
               title = 'Fieldset start widget',
               description= ('Renders XHTML fieldset open tag',),
               used_for = ('Products.PloneFormGen.contents.fieldset.FieldsetFolder',)
               )


class FieldsetEndWidget(TypesWidget):
    """
        This pseudo widget closes an XHTML fieldset.
    """

    _properties = TypesWidget._properties.copy()
    _properties.update({'macro' : 'widget_fieldset_end',
                        },)

# Register the widget with Archetypes
registerWidget(FieldsetEndWidget,
               title = 'Fieldset end widget',
               description= ('Renders XHTML fieldset end tag',),
               used_for = ('Products.PloneFormGen.contents.fieldset.FieldsetFolder',)
               )
