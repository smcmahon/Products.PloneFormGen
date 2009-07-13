from zope.interface import Interface, Attribute

class IFieldFactory(Interface):
    """IFieldFactory adapts an IPloneFormGenForm 
       and do list/add/edit/delete field.
    """
    def getField(self, fieldid):
        """Get the field that match the id or None
        """
    
    def renameField(self, oldid, newid):
        """We should have the field id synchronize with the field's input name.
           So user probally want to change this too...
        """
    
    def addField(self, fieldtype, position = -1, data = {}):
        """Create new field, using information from data
        """

    def saveField(self, fieldid, data):
        """Save a field setting, using information from data
        """
        
    def deleteField(self, fieldid):
        """Delete the comment that match the id
        """
        
    def sortField(self, fieldid, position):
        """Move a field to a new position
        """

    def copyField(self, fieldid):
        """Make a copy of fieldid right after the original
        """

