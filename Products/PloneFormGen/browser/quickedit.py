from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from Products.Five import BrowserView

from plone.memoize.view import memoize

from plone.app.layout.globals.interfaces import IViewView


class QuickEditView(BrowserView):
    """
    PFG Quick Editor (interactive form editor)
    """

    def __init__(self, context, request):
        # mark this view with IViewView so that we get
        # content actions
        alsoProvides(self, IViewView)

        self.context = context
        self.request = request
        
        # some of the Archetypes macros want controller_state
        request.controller_state = {'kwargs':{}}
    
    @memoize
    def _addableTypes(self):
        folder_factories = getMultiAdapter((self.context, self.request),
                                           name='folder_factories')
        return [atype 
                for atype in folder_factories.addable_types() 
                if atype['id'] not in ('FieldsetStart', 'FieldsetEnd', 'FieldsetFolder')
               ]

    def addablePrioritizedFields(self):
        """Return a prioritized list of the addable fields in context"""
        priorityFields = {
            'FormBooleanField': 1,
            'FormDateField': 1,
            'FormMultiSelectionField': 1,
            'FormSelectionField': 1,
            'FormStringField': 1,
            'FormTextField': 1,
            'FormIntegerField': 1,
        }


        displayPriorityFields = []
        displayTheRest = []
        for item in self._addableTypes():
            if item['id'] in priorityFields:
                displayPriorityFields.append(item)

            # XXX: this looks too weak a check to discover fields
            elif item['title'].find("Field") != -1:
                displayTheRest.append(item)

        return displayPriorityFields + displayTheRest


    def addableFieldsets(self):
        """ Return a list of fieldset markers """
        return (
            {'id':'FieldsetStart','title':'Fieldset Start','description':'Begin a fieldset'},
            {'id':'FieldsetEnd','title':'Fieldset End','description':'End a fieldset'},
        )


    def addableAdapters(self):
        """Return a list of addable adapters in context"""
        result = []
        for item in self._addableTypes():
            # XXX: this looks too weak a check to discover adapters
            if item['title'].find("Adapter") != -1:
                result.append(item)

        return result
