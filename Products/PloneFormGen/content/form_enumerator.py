###etc todo: clean up unneeded imports 

from zope.interface import implements, providedBy

import logging

from AccessControl import ClassSecurityInfo, Unauthorized
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import getExprContext

from Products.CMFPlone.utils import safe_hasattr

try:
    from Products.LinguaPlone.public import *
except ImportError:
    from Products.Archetypes.public import *

from Products.Archetypes.utils import shasattr, getRelURL
from Products.Archetypes.interfaces.field import IField

from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.configuration import zconf

from Products.TALESField import TALESString

from Products.PloneFormGen.interfaces import \
    IPloneFormGenForm, IPloneFormGenActionAdapter, IPloneFormGenThanksPage
from Products.PloneFormGen.config import \
    PROJECTNAME, fieldTypes, adapterTypes, thanksTypes, fieldsetTypes, \
    EDIT_TALES_PERMISSION, EDIT_ADVANCED_PERMISSION, BAD_IDS, FORM_ERROR_MARKER
from Products.PloneFormGen.content import validationMessages

from Products.PloneFormGen import PloneFormGenMessageFactory as _
from Products.PloneFormGen import HAS_PLONE25, HAS_PLONE30

###etc
from Globals import InitializeClass
from Products.PloneFormGen.content.form_schemata import FormFolderSchema

from types import StringTypes

if HAS_PLONE25:
  import zope.i18n


logger = logging.getLogger("PloneFormGen")    

class objFieldEnumerator:
    """ Seperate out the field enumeration to another class -
    this one is the old style contained objects checking one"""

    security       = ClassSecurityInfo()
    
    security.declarePrivate('_getFieldObjects')
    def _getFieldObjects(self, folder, objTypes=None, includeFSMarkers=False):
        """ return list of enclosed fields """

        # This function currently checks to see if
        # an object is a form field by looking to see
        # if it has an fgField attribute.

        # Make sure we look through fieldsets
        if objTypes is not None:
            objTypes = list(objTypes)[:]
            objTypes.append('FieldsetFolder')

        myObjs = []

        for obj in folder.objectValues(objTypes):
            # use shasattr to make sure we're not aquiring
            # fgField by acquisition

            # TODO: If I stick with this scheme for enable overrides,
            # I'm probably going to want to find a way to cache the result
            # in the request. _getFieldObjects potentially gets called
            # several times in a request.

            # first, see if the field enable override is set
            if shasattr(obj, 'fgTEnabled') and obj.getRawFgTEnabled():
                # process the override enabled TALES expression
                # create a context for expression evaluation
                context = getExprContext(self, obj)
                # call the tales expression, passing our custom context
                enabled = obj.getFgTEnabled(expression_context=context)
            else:
                enabled = True
            
            if enabled:
                if shasattr(obj, 'fgField'):
                    myObjs.append(obj)
                if shasattr(obj, 'fieldsetFields'):
                    myObjs += obj.fieldsetFields(objTypes, includeFSMarkers)

        return myObjs


    security.declareProtected(View, 'fgFields')
    def fgFields(self, folder, request=None, displayOnly=False):
        """ generate fields on the fly; also primes request with
            defaults if request is passed.
            if displayOnly, label fields are excluded.
        """

        if request and folder.getRawOnDisplayOverride():
            # call the tales expression, passing a custom context
            #folder.getOnDisplayOverride(expression_context=getExprContext(self, folder.aq_explicit))
            folder.getOnDisplayOverride()
            folder.cleanExpressionContext(request=request)

        myFields = []
        for obj in folder._getFieldObjects(includeFSMarkers=not displayOnly):
            if IField.isImplementedBy(obj):
                # this is a field -- not a form field -- and may be
                # added directly to the field list.
                if not displayOnly:
                    myFields.append(obj)
            else:
                if request:
                    # prime the request
                    obj.fgPrimeDefaults(request)
                #if not (displayOnly and (obj.isLabel() or obj.isFileField()) ):
                if not (displayOnly and obj.isLabel()):
                    myFields.append(obj.fgField)

        return myFields

InitializeClass(objFieldEnumerator)    

if HAS_PLONE30:
    ####etc test z3c

    from z3c.form import form, field
    from zope import interface, schema
    from z3c.form import form, field
    from z3c.form.interfaces import INPUT_MODE
    from plone.app.z3cform.wysiwyg.widget import WysiwygFieldWidget

    class IProfile(interface.Interface):
        name = schema.TextLine(title=u"Name")
        age = schema.Int(title=u"Age")
        bio = schema.Text(title=u"Bio")


class z3cFieldEnumerator:
    """ This would be the event listener that can keep all the
    object info in a dictionary or whatever"""

    security = ClassSecurityInfo()

    security.declarePrivate('_getFieldObjects')
    def _getFieldObjects(self, objTypes=None, includeFSMarkers=False):
        """ return list of enclosed fields """
        return []

    security.declareProtected(View, 'fgFields')
    def fgFields(self, request=None, displayOnly=False):
        """ return fields from dictionary"""
        return []

InitializeClass(z3cFieldEnumerator)
