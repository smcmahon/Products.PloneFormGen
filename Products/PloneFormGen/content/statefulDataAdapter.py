""" A form action adapter that saves form submissions within a data
structure for later retrieval by the form - i.e. retains state """

__author__  = 'Ben Ackland <ben@netsight.co.uk>'
__docformat__ = 'plaintext'

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from persistent.dict import PersistentDict

from Products.ATContentTypes.content.base import registerATCT
from Products.CMFPlone.utils import base_hasattr, safe_hasattr

from Products.PloneFormGen.config import *
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter
from Products.PloneFormGen.interfaces import IPloneFormGenDefaultFieldValueProvider
import logging

logger = logging.getLogger("PloneFormGen")    

class FormStatefulDataAdapter(FormActionAdapter):
    implements(IPloneFormGenDefaultFieldValueProvider)

    meta_type      = 'FormStatefulDataAdapter'
    portal_type    = 'FormStatefulDataAdapter'
    archetype_name = 'Stateful Data Adapter'

    immediate_view = 'base_view'
    default_view   = 'base_view'
    suppl_views    = ()
    
    security       = ClassSecurityInfo()

    def __init__(self, REQUEST):
        self.statefuldata = PersistentDict()
        super(FormStatefulDataAdapter, self).__init__(REQUEST)

    def onSuccess(self, fields, REQUEST=None, loopstop=False):
        """
        saves data in a stateful manner.
        """
        logger.info("FormStatefulDataAdapter: onSuccess")

        if LP_SAVE_TO_CANONICAL and not loopstop:
            # LinguaPlone functionality:
            # check to see if we're in a translated
            # form folder, but not the canonical version.
            parent = self.aq_parent
            if safe_hasattr(parent, 'isTranslation') and \
               parent.isTranslation() and not parent.isCanonical():
                # look in the canonical version to see if there is
                # a matching (by id) save-data adapter.
                # If so, call its onSuccess method
                cf = parent.getCanonical()
                target = cf.get(self.getId())
                if target.meta_type == 'FormStatefulDataAdapter':
                    target.onSuccess(fields, REQUEST, loopstop=True)
                    return

        key = self.getKey(REQUEST)
        data = {}
        for f in fields:
            if f.isFileField():
                # TODO - deal with file fields
                pass
            elif not f.isLabel():
                fname = f.fgField.getName()
                val = REQUEST.form.get(fname,None)
                data[fname] = val

        #statefuldata = getattr(self, 'statefuldata')
        self.statefuldata[key] = data
        #setattr(self, 'statefuldata', statefuldata)

    def itemsSaved(self):
        """Download the saved data
        """
        return len(self.statefuldata)

    def getStatefulData(self):
        """ Return the current data """
        return self.statefuldata.copy()

    def getKey(self, REQUEST):
        return 'balloons'

    def getDefaultFieldValue(self, field, REQUEST):
        key = self.getKey(REQUEST)
        if key in self.statefuldata.keys():
            data = self.statefuldata[key]
            if field.id in data.keys():
                return data[field.id]
        return None

registerATCT(FormStatefulDataAdapter, PROJECTNAME)
