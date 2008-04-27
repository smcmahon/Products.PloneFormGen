"""RichLabelWidget -- displays formatted text in edit form"""

# This widget isn't anything more than a placeholder. Unmodified Archetypes macros
# won't allow for a field without a label. So, to minimize intervention, this is
# handled in fg_edit_macros

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget

# The widget itself

class RichLabelWidget(TypesWidget):
    """This widget displays formatted text inside a form.
    It is probably useless outside PloneForm, since the body
    needs to be set outside the field.
    """

    # Use the base class properties, and add two of our own
    _properties = TypesWidget._properties.copy()
    _properties.update({'macro' : 'widget_richlabel',
                        },)

# Register the widget with Archetypes
registerWidget(RichLabelWidget,
               title = 'Rich label widget',
               description= ('Renders formatted text inside form',),
               used_for = ('Products.Archetypes.Field.BooleanField',)
               )
