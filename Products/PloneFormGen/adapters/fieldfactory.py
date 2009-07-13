from persistent.list import PersistentList

import OFS.subscribers
from OFS.event import ObjectClonedEvent
from zope import event, interface, component
from zope.lifecycleevent import ObjectCopiedEvent

from Products.CMFCore.utils import getToolByName

from Products.PloneFormGen.interfaces import IPloneFormGenForm
from Products.PloneFormGen.adapters.interfaces import IFieldFactory

def generate_id(target, old_id):
    """Copy from plone.app.contentrules.actions.copy 
    """
    taken = getattr(target, 'has_key', None)
    if taken is None:
        item_ids = set(target.objectIds())
        taken = lambda x: x in item_ids
    if not taken(old_id):
        return old_id
    idx = 1
    while taken("%s.%d" % (old_id, idx)):
        idx += 1
    return "%s.%d" % (old_id, idx)

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
    
    def addField(self, fieldtype, position = -1, data = {}):
        """Create new field, using information from data
        """
        #TODO: Handle exception
        fieldid = self.context.generateUniqueId(fieldtype)
        self.context.invokeFactory(fieldtype, id = fieldid, **data)
        if position != -1:
            self.context.moveObject(fieldid, position)
        return fieldid

    def saveField(self, fieldid, data):
        """Save a field setting, using information from data
        """
        #TODO: This is specified for Archetype object only,
        #      We should find another implement way to support more general obj.
        field = self.getField(fieldid)
        if field is None:
            raise "Unable to find %s in %s" %(fieldid, self.context)
        errors = {}
        REQUEST = None
        #Do validate
        for key in data.keys():
            value = data[key]
            atfield = field.schema.get(key, None)
            if atfield is not None:
                atfield.validate(instance=field,
                                 value=value,
                                 errors=errors,
                                 REQUEST=REQUEST)
        #If not errors: Do update
        if not errors:
            for key in data.keys():
                atfield = field.schema.get(key, None)
                if atfield is not None:
                    mutator = atfield.getMutator(field)
                    #TODO: try .. catch here ? things should be fine 
                    mutator(data[key])
        return errors

    def deleteField(self, fieldid):
        """Delete the comment that match the id
        """
        self.context.manage_delObjects(fieldid)
        
    def moveField(self, fieldid, position):
        """Move a field to a new position
        """
        #TODO: the function (on base ordered folder class) seems not work 
        #      in the way it should be. I need to do +1 on position
        self.context.moveObject(fieldid, position+1)
        
    def copyField(self, fieldid):
        """Make a copy of fieldid right after the original
        """
        obj = self.getField(fieldid)
        target = self.context

        obj._notifyOfCopyTo(target, op=0)
        old_id = obj.getId()
        new_id = generate_id(self.context, old_id)
        
        orig_obj = obj
        obj = obj._getCopy(target)
        obj._setId(new_id)
        
        event.notify(ObjectCopiedEvent(obj, orig_obj))

        target._setObject(new_id, obj)
        obj = target._getOb(new_id)
        obj.wl_clearLocks()

        obj._postCopy(target, op=0)

        OFS.subscribers.compatibilityCall('manage_afterClone', obj, obj)
        
        event.notify(ObjectClonedEvent(obj))
        
        self.moveField(new_id, self.getFieldPos(old_id)+1)
        return new_id
