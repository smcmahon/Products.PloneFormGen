from zope.interface import Interface, Attribute

# This is just a marker inteface; PFG identifies adapters by asking
# contained objects if they provide this interface.
#
# Note that marking an object type with this interface 
# does not automatically put it on the "add" menu. That
# needs to be done via portal_types.

class IPloneFormGenDefaultFieldValueProvider(Interface):
    """statefulActionAdapter interface
    """
    def getDefaultFieldValue(field, REQUEST):
        """
        get the previously stored value (if it exists) or None for the field
        object 'field'

        REQUEST is used to determine a unique identifier for the current user
        (this might be their userid or a unique id within a cookie or
        a session-related id of some kind)
        """
