from urllib import quote_plus

from Acquisition import aq_inner, aq_parent
from zope.component import getMultiAdapter, queryUtility
from zope.interface import alsoProvides
from Products.Five import BrowserView
from Products.CMFCore.Expression import createExprContext

from Products.CMFCore.utils import getToolByName
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.view import memoize

from plone.app.layout.globals.interfaces import IViewView
from Products.PloneFormGen import PloneFormGenMessageFactory as _


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
        results = []
        for t in self.context.allowedContentTypes():
            typeId = t.getId()
            if t.id not in ('FieldsetStart', 'FieldsetEnd', 'FieldsetFolder'):
                results.append({
                    'id': typeId,
                    'title': t.Title(),
                    'description': t.Description()
                })
        return results

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
            {'id':'FieldsetStart','title':_(u'Fieldset Start'),'description':_(u'Begin a fieldset')},
            {'id':'FieldsetEnd','title':_(u'Fieldset End'),'description':_(u'End a fieldset')},
        )


    def addableAdapters(self):
        """Return a list of addable adapters in context"""
        result = []
        for item in self._addableTypes():
            # XXX: this looks too weak a check to discover adapters
            if item['title'].find("Adapter") != -1:
                result.append(item)

        return result
