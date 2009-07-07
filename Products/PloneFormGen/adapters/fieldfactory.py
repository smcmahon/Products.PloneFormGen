from persistent.list import PersistentList
from zope import interface, component

import OFS.subscribers
from OFS.event import ObjectClonedEvent

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
        self.fieldids = context.objectIds()

    def getField(self, fieldid):
        """Get the field that match the id or None
        """
        if not fieldid in self.fieldids:
            return None
        return getattr(self.context, fieldid)
    
    def getFieldPos(self, fieldid):
        """Return the current position of the field in the form
        """
        if not fieldid in self.fieldids:
            return -1
        return self.fieldids.index(fieldid)

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
        #TODO: This is specified for Archetype object only,
        #      We should find another implement way to support more general obj.
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
        
    def copyField(self, fieldid):
        """Make a copy of fieldid right after the original
        """
        obj = self.getField(fieldid)
        target = self.context

        obj._notifyOfCopyTo(target, op=0)
        old_id = obj.getId()
        new_id = 'copy_of_%s' %old_id
        
        orig_obj = obj
        obj = obj._getCopy(target)
        obj._setId(new_id)
        
        notify(ObjectCopiedEvent(obj, orig_obj))

        target._setObject(new_id, obj)
        obj = target._getOb(new_id)
        obj.wl_clearLocks()

        obj._postCopy(target, op=0)

        OFS.subscribers.compatibilityCall('manage_afterClone', obj, obj)
        
        notify(ObjectClonedEvent(obj))
        
