from Acquisition import aq_parent, aq_inner
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from Products.CMFPlone.interfaces import IFactoryTool

from Products.PloneFormGen import interfaces


@adapter(interfaces.IPloneFormGenActionAdapter, IObjectAddedEvent)
def form_adapter_pasted(form_adapter, event):
    """If an action adapter is pasted into the form, add it to the form's
       list of active adapters. We only need to do anything if the action
       adapter isn't newly created in the portal_factory.
    """
    form_adapter = aq_inner(form_adapter)
    if IFactoryTool.providedBy(aq_parent(aq_parent(form_adapter))):
        return

    form = aq_parent(form_adapter)
    adapters = list(form.actionAdapter)
    if form_adapter.id not in adapters:
        adapters.append(form_adapter.id)
        form.setActionAdapter(adapters)


@adapter(interfaces.IPloneFormGenActionAdapter, IObjectMovedEvent)
def form_adapter_moved(form_adapter, event):
    """If an active action adapter is renamed, keep it active.

    Instead of renaming, some more moves are possible, like moving from
    one form to another, though that is unlikely.  We can handle it
    all though.

    Note that in a pure rename, event.oldParent is the same as
    event.newParent.  One of them could be None.  They may not always
    be forms.
    """
    form_adapter = aq_inner(form_adapter)
    if IFactoryTool.providedBy(aq_parent(aq_parent(form_adapter))):
        return

    if not event.oldParent:
        # We cannot know if the adapter was active, so we do nothing.
        pass
    try:
        adapters = list(event.oldParent.actionAdapter)
    except AttributeError:
        # no Form Folder, probably factory tool
        return
    was_active = event.oldName in adapters
    if was_active:
        # deactivate the old name
        adapters.remove(event.oldName)
        event.oldParent.setActionAdapter(adapters)
    if not was_active:
        # nothing to do
        return
    if event.newParent:
        try:
            adapters = list(event.newParent.actionAdapter)
        except AttributeError:
            # no Form Folder, probably factory tool
            return
        else:
            if event.newName not in adapters:
                adapters.append(event.newName)
                event.newParent.setActionAdapter(adapters)
