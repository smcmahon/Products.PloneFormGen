from Acquisition import aq_inner
from zope.component import getMultiAdapter
from Products.Five import BrowserView


class QuickEditView(BrowserView):
    """
    PFG Quick Editor (interactive form editor)
    """

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request
        request.controller_state = {'kwargs':{}}
        folder_factories = getMultiAdapter((self.context, self.request),
                                           name='folder_factories')
        self.addable_types = folder_factories.addable_types()

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
        for item in self.addable_types:
            if item['id'] in priorityFields:
                displayPriorityFields.append(item)

            # XXX: this looks too weak a check to discover fields
            elif item['title'].find("Field") != -1:
                displayTheRest.append(item)

        return displayPriorityFields + displayTheRest

    def addableAdapters(self):
        """Return a list of addable adapters in context"""
        result = []
        for item in self.addable_types:
            # XXX: this looks too weak a check to discover adapters
            if item['title'].find("Adapter") != -1:
                result.append(item)

        return result
