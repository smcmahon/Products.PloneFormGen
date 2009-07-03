from persistent.list import PersistentList
from zope import interface, component

from Products.CMFCore.utils import getToolByName

from Products.PloneFormGen.interfaces import IPloneFormGenForm
from Products.PloneFormGen.adapters.interfaces import IFieldFactory

class FieldFactory(object):
    """Adapter that work with form's fields.    
    """

    component.adapts(IPloneFormGenForm)
    interface.implements(IFieldFactory)
    
    def __init__(self, context):
        self.context = context

    def getField(self, fieldid):
        """Get the field that match the id or None
        """
        return getattr(self.context, fieldid)
    
    def renameField(self, oldid, newid):
        """We should have the field id synchronize with the field's input name.
           So user probally want to change this too...
        """
        folder.manage_renameObject(id=oldid, new_id=newid)        
        return None
    
    def addField(self, fieldtype, position = -1, **data):
        """Create new field, using information from data
        """
        #TODO: Handle exception
        fieldid = self.context.invokeFactory(fieldtype, **data)
        if position != -1:
            self.sortField(fieldid, position)
        return None

    def saveField(self, fieldid, **data):
        """Save a field setting, using information from data
        """
        field = self.getField(fieldid)
        if field is None:
            raise "Unable to find %s in %s" %(fieldid, self.context)
        errors = []
        REQUEST = None
        #Do validate
        for key in data.keys():
            value = data[key]
            atfield = schema.get(key, None)
            if atfield:
                field.validate(instance=field, value=value, errors=errors, REQUEST=REQUEST)
        #If not errors: Do update
        if not errors:
            for key in data.keys():
                value = data[key]
                mutator = atfield.getMutator(field)
                #TODO: try .. catch here ? things should be fine 
                mutator(data)
        return errors

    def deleteField(self, fieldid):
        """Delete the comment that match the id
        """
        self.context.manage_delObjects(fieldid)
        return None
        
    def sortField(self, fieldid, position):
        """Move a field to a new position
        """
        self.context.moveObject(fieldid, position)
        return None
