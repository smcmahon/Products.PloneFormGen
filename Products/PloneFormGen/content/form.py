"""FormFolder -- A container for form fields"""

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

###etc   split out the schemata to make it more managable and contain the plone version dependent changing z3c or archetype fields part of folder in an enumerator class

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
from Products.PloneFormGen.content.form_schemata import FormFolderSchema
from Products.PloneFormGen.content.form_enumerator import *

from types import StringTypes

if HAS_PLONE25:
  import zope.i18n


logger = logging.getLogger("PloneFormGen")    

if HAS_PLONE30:
    # Plone 3 switches the schema tab widget to a select box when
    # the number of schemata is > 6. IMHO, this has worse usability
    # than packing the default schema.
    # Also, as of P3.0, rich text fields on non-default schema
    # still don't function.
    FormFolderSchema['formPrologue'].schemata = 'default'
    FormFolderSchema['formEpilogue'].schemata = 'default'

#finalizeATCTSchema(ATFolderSchema, folderish=True, moveDiscussion=False)

class FormFolder(ATFolder):
    """A folder which can contain form fields."""

    implements(IPloneFormGenForm)

    schema         =  FormFolderSchema

    content_icon   = 'Form.gif'
    meta_type      = 'FormFolder'
    portal_type    = 'FormFolder'
    archetype_name = 'Form Folder'

    if HAS_PLONE30:
        default_view   = immediate_view = 'fg_base_view_p3'
    else:
        default_view   = immediate_view = 'fg_base_view'

    suppl_views = ()

    typeDescription= 'A folder which creates a form view from contained form fields.'

    # XXX We should do this with a tool so that others may add fields
    allowed_content_types = fieldTypes + adapterTypes + thanksTypes + fieldsetTypes + ('Document', 'Image')

    security       = ClassSecurityInfo()

    def initEnumerator(self):

        if HAS_PLONE30:
        ###etc umcomment when its written!
#        self.fields = z3cFieldEnumerator(self)
            self.fields = objFieldEnumerator()
        else:
            self.fields = objFieldEnumerator()

    security.declarePrivate('_getFieldObjects')
    def _getFieldObjects(self, objTypes=None, includeFSMarkers=False):
        """ return list of enclosed fields """
        if not hasattr(self,'fields'):
            self.initEnumerator()
        return self.fields._getFieldObjects(self, objTypes=None, includeFSMarkers=False)


    security.declarePrivate('findFieldObjectByName')
    def findFieldObjectByName(self, name):
        """ Find a form field object by name,
            searching fieldsets if necessary.
            This is used by fieldsBase vocabulary fields
            to find the form field instance associated
            with a field.
        """
       
        for obj in self._getFieldObjects():
            if obj.__name__ == name:
               return obj
        return None        


    security.declarePrivate('cleanExpressionContext')
    def cleanExpressionContext(self, object=None, request=None):
        """ clean the expression context of references to object """

        # When a TALES expression is evaluated, a copy
        # of the expression context for the object is stored in the request
        # in case it's needed again.
        # The problem is that if we allow this to get stored for PFG's
        # overrides, it will not meet the needs of template code that
        # assumes a more complete context.
        #
        # This function's job is to clear the expression context cache for
        # the current object.
        #
        # Note that this doesn't need to be called if there's no danger
        # of the expression context being re-used in a template.

        if object is None:
            object = self
        
        if request:
            cache = request.get('_ec_cache', None)
            if cache:
                if cache.has_key( id(object) ):
                    del cache[ id(object) ]
        

    security.declareProtected(View, 'fgFields')
    def fgFields(self, request=None, displayOnly=False):
        """ generate fields on the fly; also primes request with
            defaults if request is passed.
            if displayOnly, label fields are excluded.
        """
        if not hasattr(self,'fields'):
            self.initEnumerator()
        return self.fields.fgFields(self, request=None, displayOnly=False)


    security.declareProtected(View, 'fgvalidate')
    def fgvalidate(self, REQUEST=None, errors=None, data=None, metadata=None):
        """Validates the field data from the request.
        """

        _marker = []
        if errors is None:
            errors = {}
        if errors:
            return errors

        # Get all the form fields. Exclude actual IField fields.
        fields = [fo for fo in self._getFieldObjects() if not IField.isImplementedBy(fo)]

        for obj in fields:
            field = obj.fgField

            result = field.widget.process_form(self, field, REQUEST.form, empty_marker=_marker)

            if result is None or result is _marker:
                #XXX Make this smarter
                value = ''
            else:
                value = result[0]

            # workaround what I consider a Zope marshalling error: the production
            # of lists like ['one', ''] and [''] for list fields.
            # no need to worry about polymorphism here, as this is a very particular
            # case.        
            if isinstance(value, type([])) and len(value) and \
              (type(value[-1]) in StringTypes) and (len(value[-1]) == 0):
                value.pop()
                
            # eliminate trailing white space in string types.
            if safe_hasattr(value, 'rstrip'):
                newvalue = value.rstrip()
                if newvalue != value:
                    value = newvalue
                    # since strings are immutable, we have to manually store it back to the request
                    if safe_hasattr(REQUEST, 'form'):
                        REQUEST.form[obj.getFieldFormName()] = value                        

            # Archetypes field validation
            res = field.validate(instance=self, value=value, errors=errors, REQUEST=REQUEST)

            if not res:
                # give the field itself an opportunity to validate.
                res = obj.specialValidator(value, field, REQUEST, errors)

            if res:
                errors[field.getName()] = validationMessages.cleanupMessage(res, self.REQUEST, self)
            elif shasattr(obj, 'getFgTValidator') and obj.getRawFgTValidator():
                # process the override validator TALES expression

                # create a context for expression evaluation
                context = getExprContext(self, obj)
                
                # put this field's input (from request) into the context globals
                # as 'value'
                context.setGlobal('value', REQUEST.form.get(obj.getFieldFormName(), None))
                
                # call the tales expression, passing our custom context
                cerr = obj.getFgTValidator(expression_context=context)
                if cerr:
                    errors[field.getName()] = cerr

        if not errors:
            if self.getRawAfterValidationOverride():
                # evaluate the override.
                # In case we end up traversing to a template,
                # we need to make sure we don't clobber
                # the expression context.
                self.getAfterValidationOverride()
                self.cleanExpressionContext(request=self.REQUEST)

            adapters = self.getRawActionAdapter()
            for adapter in adapters:
                actionAdapter = getattr(self.aq_explicit, adapter, None)
                if actionAdapter is None:
                    logger.warn("Designated action adapter '%s' is missing; ignored." % adapter)
                else:
                    # Now, see if we should execute it.
                    # Check to see if execCondition exists and has contents
                    if safe_hasattr(actionAdapter, 'execCondition') and \
                      len(actionAdapter.getRawExecCondition()):
                        # evaluate the execCondition.
                        # create a context for expression evaluation
                        context = getExprContext(self, actionAdapter)
                        doit = actionAdapter.getExecCondition(expression_context=context)
                    else:
                        # no reason not to go ahead
                        doit = True

                    if doit:
                        result = actionAdapter.onSuccess(fields, REQUEST=REQUEST)
                        if type(result) is type({}) and len(result):
                            # return the dict, which hopefully uses
                            # field ids or FORM_ERROR_MARKER for keys
                            return result

        return errors


    security.declareProtected(View, 'fgGetSuccessAction')
    def fgGetSuccessAction(self):
        """
             Returns string id of success action template or script.
             Controller will traverse to this on successful validation.
         """

        if safe_hasattr(self, 'thanksPageOverride'):
            s = self.getThanksPageOverride()
            if s:
                return s

        s = getattr(self, 'thanksPage', None)
        if s:
            obj = getattr(self, s, None)
            if obj:
                return 'traverse_to:string:%s' % obj.getId()
            
        return 'traverse_to:string:fg_result_view'


    # security.declareProtected(ModifyPortalContent, 'getRawActionAdapter')
    def getRawActionAdapter(self):
        """ Returns selected action adapters as tuple """

        # this method translates a string actionAdapter
        # attribute from a previous version into a tuple        
        try:
            self.actionAdapter + ''
            if self.actionAdapter:
                return (self.actionAdapter,)
            else:
                return ()
        except:
            return self.actionAdapter


    security.declareProtected(ModifyPortalContent, 'actionAdaptersDL')
    def actionAdaptersDL(self):
        """ returns Display List (id, title) tuples of contained adapters """

        # an adapter provides IPloneFormGenActionAdapter
        allAdapters = [(obj.getId(), obj.title) for obj in self.objectValues() if IPloneFormGenActionAdapter in providedBy(obj)]

        if allAdapters:
            return DisplayList( allAdapters )

        return DisplayList()            
#        else:
#            if HAS_PLONE25:
#                return DisplayList(
#                    [('', _(u'vocabulary_none_text', u'None')),]
#                    )
#            else:
#                return DisplayList(
#                    [('', self.translate( msgid='vocabulary_none_text', domain='ploneformgen', default='None')),]
#                    )


    security.declareProtected(ModifyPortalContent, 'addActionAdapter')
    def addActionAdapter(self, id):
        """ activate action adapter with id == id """
        
        aa = list(self.getRawActionAdapter())
        if id not in aa:
            aa.append(id.decode(self.getCharset()))
        self.actionAdapter = aa
        

    security.declareProtected(ModifyPortalContent, 'fgFieldsDisplayList')
    def fgFieldsDisplayList(self, withNone=False, noneValue='', objTypes=None):
        """ returns display list of fields """

        myFields = []
        if withNone:
            if HAS_PLONE25:
                myFields.append( (noneValue, _(u'vocabulary_none_text', u'None')) )
            else:
                myFields.append( (noneValue, self.translate( msgid='vocabulary_none_text', domain='ploneformgen', default='None')) )

        for obj in self._getFieldObjects(objTypes):
            if isinstance(obj.title, unicode):
                myFields.append( (obj.getId(), obj.title) )
            else:
                myFields.append( (obj.getId(), obj.title.decode(self.getCharset())) )

        return DisplayList( myFields )


    security.declareProtected(ModifyPortalContent, 'thanksPageVocabulary')
    def thanksPageVocabulary(self):
        """ returns a DisplayList of contained page-ish documents """

        propsTool = getToolByName(self, 'portal_properties')
        siteProperties = getattr(propsTool, 'site_properties')
        defaultPageTypes = siteProperties.getProperty('default_page_types')

        if HAS_PLONE25:
            tpages = [('', _(u'vocabulary_none_text', u'None')),]
        else:
            tpages = [('', self.translate( msgid='vocabulary_none_text', domain='ploneformgen', default='None')),]

        for obj in self.objectValues():
            if IPloneFormGenThanksPage in providedBy(obj) or \
              getattr(obj.aq_explicit, 'portal_type', 'none') in defaultPageTypes:
                tpages.append( (obj.getId(), obj.title) )
                
        return DisplayList( tpages )


    ###
    # A few widgets (TextArea and RichWidget in particular) call the content
    # object rather than the field for this method. IMHO, this is unnecessary,
    # and should be fixed in the Widget. Meanwhile, this hack ...
    #
    security.declareProtected(View, 'isBinary')
    def isBinary(self, key):
        """Return whether a field contains binary data.
        """

        try:
            res = BaseObject.isBinary(self, key)
        except (TypeError, AttributeError):
            res = 0
        return res


    # The Archetypes file.pt macro tries -- for reasons I don't
    # really understand -- to call the field's accessor.
    # So, let's supply this as a harmless one when necessary.
    def nullAccessor(self, **kwargs):
        return None


    # Don't show the display options; doesn't make sense
    # when there are no real options
    def canSetDefaultPage(self):
        return False


    security.declarePrivate('_pfFixup')
    def _pfFixup(self, obj):
    
        # the creation of contained objects in initializeArchetypes
        # leaves catalog orphans for the portal_factory objects.
        #
        # this solves the problem by removing them from the
        # portal_catalog and uid_catalog,
        # hopefully not causing other problems in the process.

        if 'portal_factory' in obj.getPhysicalPath():
            # remove from portal_catalog
            obj.unindexObject()

            # remove from uid_catalog
            uid_catalog = getToolByName(self, 'uid_catalog', None)
            uid_catalog.uncatalog_object( getRelURL(self, obj.getPhysicalPath()) )

        else:
            obj.reindexObject()
        

    def initializeArchetype(self, **kwargs):
        """ Create sample content that may help folks
            figure out how this gadget works.
        """

        ATFolder.initializeArchetype(self, **kwargs)

        if HAS_PLONE25:
            self.setSubmitLabel(zope.i18n.translate(_(u'pfg_formfolder_submit', u'Submit'), context=self.REQUEST))
            self.setResetLabel(zope.i18n.translate(_(u'pfg_formfolder_reset', u'Reset'), context=self.REQUEST))
        else:
            self.setSubmitLabel(self.translate(
                                  msgid='pfg_formfolder_submit',
                                  domain='ploneformgen',
                                  default='Submit'))
            self.setResetLabel(self.translate(
                                  msgid='pfg_formfolder_reset',
                                  domain='ploneformgen',
                                  default='Reset'))

        oids = self.objectIds()

        haveMailer = False
        if 'mailer' not in oids:
            # create a mail action
            try:
                self.invokeFactory('FormMailerAdapter','mailer')
                mailer = self['mailer']

                if HAS_PLONE25:
                    mailer.setTitle(zope.i18n.translate(_(u'pfg_mailer_title', u'Mailer'), context=self.REQUEST))
                    mailer.setDescription(zope.i18n.translate(_(u'pfg_mailer_description', u'E-Mails Form Input'), context=self.REQUEST))
                else:
                    mailer.setTitle(self.utranslate(
                            msgid='pfg_mailer_title',
                            domain='ploneformgen',
                            default='Mailer'))
                    mailer.setDescription(self.utranslate(
                            msgid='pfg_mailer_description',
                            domain='ploneformgen',
                            default='E-Mails From Input'))

                self._pfFixup(mailer)

                self.actionAdapter = ('mailer',)
                haveMailer = True
            except Unauthorized:
                logger.warn('User not authorized to create mail adapters. Form Folder created with no action adapter.')

        if 'replyto' not in oids:
            # create a replyto field
            self.invokeFactory('FormStringField','replyto')
            obj = self['replyto']
            obj.fgField.__name__ = 'replyto'

            if HAS_PLONE25:
                obj.setTitle(zope.i18n.translate(_(u'pfg_replytofield_title', u'Your E-Mail Address'), context=self.REQUEST))
            else:
                obj.setTitle(self.translate(
                                  msgid='pfg_replytofield_title',
                                  domain='ploneformgen',
                                  default='Your E-Mail Address'))

            obj.fgField.required = True
            obj.setFgStringValidator('isEmail')
            obj.setFgTDefault('here/memberEmail')
            obj.setFgDefault('dynamically overridden')

            self._pfFixup(obj)

            if haveMailer:
                mailer.replyto_field = 'replyto'
        
        if 'topic' not in oids:
            # create a subject field
            self.invokeFactory('FormStringField','topic')
            obj = self['topic']
            obj.fgField.__name__ = 'topic'

            if HAS_PLONE25:
                obj.setTitle(zope.i18n.translate(_(u'pfg_topicfield_title', u'Subject'), context=self.REQUEST))
            else:
                obj.setTitle(self.translate(
                                  msgid='pfg_topicfield_title',
                                  domain='ploneformgen',
                                  default='Subject'))

            obj.fgField.required = True

            self._pfFixup(obj)

            if haveMailer:
                mailer.subject_field = 'topic'
        
        if 'comments' not in oids:
            # create a comments field
            self.invokeFactory('FormTextField','comments')
            obj = self['comments']
            obj.fgField.__name__ = 'comments'

            if HAS_PLONE25:
                obj.setTitle(zope.i18n.translate(_(u'pfg_commentsfield_title', u'Comments'), context=self.REQUEST))
            else:
                obj.setTitle(self.translate(
                                msgid='pfg_commentsfield_title',
                                domain='ploneformgen',
                                default='Comments'))

            obj.fgField.required = True

            self._pfFixup(obj)

        
        if 'thank-you' not in oids:
            # create a thanks page
            self.invokeFactory('FormThanksPage','thank-you')
            obj = self['thank-you']

            if HAS_PLONE25:
                obj.setTitle(zope.i18n.translate(_(u'pfg_thankyou_title', u'Thank You'), context=self.REQUEST))
                obj.setDescription(zope.i18n.translate(_(u'pfg_thankyou_description', u'Thanks for your input.'), context=self.REQUEST))
            else:
                obj.setTitle(self.translate(
                                    msgid='pfg_thankyou_title',
                                    domain='ploneformgen',
                                    default='Thank You'))
                obj.setDescription(self.translate(
                                    msgid='pfg_thankyou_description',
                                    domain='ploneformgen',
                                    default='Thanks for your input.'))

            self._pfFixup(obj)

            self.thanksPage = 'thank-you'
                    

    security.declareProtected(View, 'memberFullName')
    def memberFullName(self):
        """ convenience method meant for use in default overrides.
            returns full name of authenticated user, if available,
            empty string otherwise.
        """
    
        pm = getToolByName(self, 'portal_membership')
        member = pm.getAuthenticatedMember()

        return member.getProperty('fullname', '')


    security.declareProtected(View, 'memberEmail')
    def memberEmail(self):
        """ convenience method meant for use in default overrides.
            returns e-mail address of authenticated user, if available,
            empty string otherwise.
        """
    
        pm = getToolByName(self, 'portal_membership')
        member = pm.getAuthenticatedMember()
        
        return member.getProperty('email', '')


    security.declareProtected(View, 'memberId')
    def memberId(self):
        """ convenience method meant for use in default overrides.
            returns login id of authenticated user, if available,
            empty string otherwise.
        """
    
        pm = getToolByName(self, 'portal_membership')
        if pm.isAnonymousUser():
            return ''

        member = pm.getAuthenticatedMember()
        return member.id


    # security is inherited
    def checkIdAvailable(self, id):
        """ Expands on ATFolder by checking for ids known to cause problems.
            This includes ids of objects in all fieldsets.
        """
        
        result = ATFolder.checkIdAvailable(self, id)
        if result:
            result = id not in BAD_IDS
            if result:
                # check the fieldsets
                fieldsets = self.objectValues('FieldsetFolder')
                for fs in fieldsets:
                    if id in fs.objectIds():
                        return False
                
        return result
        

    security.declareProtected(View, 'formFolderObject')
    def formFolderObject(self):
        """ Find form folder by acquisition """
        
        return self

 
    security.declareProtected(ModifyPortalContent, 'setFormPrologue')
    def setFormPrologue(self, value, **kw):
        """ Set formPrologue """
        
        # workaround a Kupu oddity: saving '<p>&nbsp;</p>' for
        # and empty input
        if value.strip() == '<p>&nbsp;</p>':
            self.formPrologue = ''
        else:
            self.formPrologue = value


    security.declareProtected(ModifyPortalContent, 'setFormPrologue')
    def setFormEpilogue(self, value, **kw):
        """ Set formEpilogue """
        
        # workaround a Kupu oddity: saving '<p>&nbsp;</p>' for
        # and empty input
        if value.strip() == '<p>&nbsp;</p>':
            self.formEpilogue = ''
        else:
            self.formEpilogue = value

registerATCT(FormFolder, PROJECTNAME)

