from zope.interface import Interface

# This is just a marker inteface; PFG identifies adapters by asking
# contained objects if they provide this interface.
#
# Note that marking an object type with this interface 
# does not automatically put it on the "add" menu. That
# needs to be done via portal_types.

class IPloneFormGenActionAdapter(Interface):
    """actionAdapter marker interface
    """
