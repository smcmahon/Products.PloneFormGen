import logging

from Acquisition import aq_parent, aq_inner
from zope.component import adapter
from zope.app.container.interfaces import IObjectAddedEvent

from Products.CMFPlone.interfaces import IFactoryTool

from Products.PloneFormGen import interfaces, implementedOrProvidedBy

@adapter(interfaces.IPloneFormGenActionAdapter, IObjectAddedEvent)
def form_adapter_pasted(form_adapter, event):
    """If an action adapter is pasted into the form, add it to the form's 
       list of active adapters. We only need to do anything if the action
       adapter isn't newly created in the portal_factory.
    """
    form_adapter = aq_inner(form_adapter)
    if implementedOrProvidedBy(IFactoryTool, aq_parent(aq_parent(form_adapter))):
        return
        
    form = aq_parent(form_adapter)
    adapters = list(form.actionAdapter)
    if form_adapter.id not in adapters:
        adapters.append(form_adapter.id)
        form.setActionAdapter(adapters)
