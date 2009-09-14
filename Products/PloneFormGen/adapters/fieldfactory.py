from persistent.list import PersistentList
from Acquisition import aq_parent, aq_inner, aq_base

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

    def getField(self, fieldpath):
        """Get the field that match the id or None
        """
        try:
            return self.context.unrestrictedTraverse(fieldpath.replace(':','/'))
        except:
            #TODO: should have: if debug is on then print trace back
            return None
    
    def getFieldPos(self, field):
        """Return the current position of the field in the form
        """
        return field.getObjPositionInParent()

#    def renameField(self, oldid, newid):
#        """We should have the field id synchronize with the field's input name.
#           So user probally want to change this too...
#        """
#        folder.manage_renameObject(id=oldid, new_id=newid)        
#        return None
    
    def addField(self, fieldtype, containerpath = "", position = -1, data = {}):
        """Create new field, using information from data
        """
        #TODO: Handle exception
        fieldid = self.context.generateUniqueId(fieldtype)
        container = self.context
        if containerpath:
            container = self.getField(containerpath)
        container.invokeFactory(fieldtype, id = fieldid, **data)
        fieldpath = ""
        if containerpath:
            fieldpath = "%s:%s" %(containerpath, fieldid)
        else:
            fieldpath = fieldid
        if position != -1:
            self.moveField(fieldpath, containerpath, position)
        return fieldpath

    def saveField(self, fieldpath, data):
        """Save a field setting, using information from data
        """
        #TODO: This is specified for Archetype object only,
        #      We should find another implement way to support more general obj.
        field = self.getField(fieldpath)
        if field is None:
            raise "Unable to find %s in %s" %(fieldpath, self.context)
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
        #TODO: Some errors raised becaused of the id field in the request :|
        if data.has_key('id'):
            data.pop('id')
        if not errors:
            for key in data.keys():
                atfield = field.schema.get(key, None)
                if atfield is not None:
                    mutator = atfield.getMutator(field)
                    #TODO: try .. catch here ? things should be fine 
                    mutator(data[key])
        return errors

    def deleteField(self, fieldpath):
        """Delete the comment that match the id
        """
        field = self.getField(fieldpath)
        if field is None:
            raise "Field not found"
        parent = aq_inner(aq_parent(field))
        fieldid = fieldpath.split(":")[-1]
        parent.manage_delObjects(fieldid)
        
    def moveField(self, fieldpath, containerpath, position):
        """Move a field to a new position
        """
        field = self.getField(fieldpath)
        if field is None:
            raise "Field not found" 
        fieldid = field.getId()
        if containerpath: 
            container = self.getField(containerpath)
        else:
            container = self.context
        parent = aq_parent(aq_inner(field))
        if aq_base(container) is aq_base(parent):
            container.moveObject(fieldid, position)
        else:
            container.manage_pasteObjects(parent.manage_cutObjects(field.getId()))
            container.moveObject(fieldid, position)
        #Reindex related objects
        for item in container.items():
            item[1].reindexObject(idxs = ['getObjPositionInParent'])
        if aq_base(container) is not aq_base(parent):
            for item in parent.items():
                item[1].reindexObject(idxs = ['getObjPositionInParent'])

    def copyField(self, fieldpath):
        """Make a copy of fieldpath right after the original
        """
        obj = self.getField(fieldpath)
        target = aq_parent(aq_inner(obj))

        obj._notifyOfCopyTo(target, op=0)
        old_id = obj.getId()
        new_id = generate_id(target, old_id)
        
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
        
        formpath = ":".join(self.context.getPhysicalPath())
        containerpath = ":".join(target.getPhysicalPath())
        objpath = ":".join(obj.getPhysicalPath())
        self.moveField(objpath[len(formpath)+1:], containerpath[len(formpath)+1:], \
                       self.getFieldPos(orig_obj)+1)
        return new_id
