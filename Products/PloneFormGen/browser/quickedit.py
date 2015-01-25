from urllib import quote_plus

from zope.interface import alsoProvides
from Products.Five import BrowserView

from plone.memoize.view import memoize

from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.PloneFormGen import PloneFormGenMessageFactory as _
from Products.PloneFormGen import HAVE_43


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
            if typeId not in ('FieldsetStart', 'FieldsetEnd', 'FieldsetFolder'):
                results.append({
                    'id': quote_plus(typeId),
                    'title': t.Title(),
                    'description': t.Description()
                })
        return results

    def addableFields(self):
        results = set()
        at_tool = getToolByName(self.context, 'archetype_tool')
        for t in self.context.allowedContentTypes():
            if t.product == 'PloneFormGen':
                type_spec = at_tool.lookupType(t.product, t.content_meta_type)
                results |= set(type_spec['schema'].fields())
        return list(results)

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

    def iconExt(self):
        """ icon extension for this version """

        if HAVE_43:
            return u"png"
        else:
            return u"gif"

