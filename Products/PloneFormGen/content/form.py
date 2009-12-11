"""FormFolder -- A container for form fields"""

__author__ = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

from zope.interface import implements

import logging
import transaction

from ZPublisher.Publish import Retry
from zExceptions import Redirect

from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager
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

try:
    from plone.app.folder.folder import ATFolderSchema, ATFolder
except ImportError:
    ### BBB for < Plone 4
    from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder

from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.configuration import zconf

from Products.TALESField import TALESString

from Products.PloneFormGen.interfaces import \
    IPloneFormGenForm, IPloneFormGenActionAdapter, IPloneFormGenThanksPage
from Products.PloneFormGen.config import \
    PROJECTNAME, \
    EDIT_TALES_PERMISSION, EDIT_ADVANCED_PERMISSION, BAD_IDS
from Products.PloneFormGen.content import validationMessages

from Products.PloneFormGen import PloneFormGenMessageFactory as _
from Products.PloneFormGen import HAS_PLONE30
from Products.PloneFormGen import implementedOrProvidedBy


try:
    import plone.protect
    HAS_PLONE_PROTECT = True
except ImportError:
    HAS_PLONE_PROTECT = False

from types import StringTypes

import zope.i18n

logger = logging.getLogger("PloneFormGen")

FormFolderSchema = ATFolderSchema.copy() + Schema((
    StringField('submitLabel',
        required=0,
        searchable=0,
        default="Submit",
        widget=StringWidget(
            label="Submit Button Label",
            label_msgid = "label_submitlabel_text",
            description_msgid = "help_submitlabel_text",
            i18n_domain = "ploneformgen",
            ),
        ),
    BooleanField('useCancelButton',
        required=0,
        searchable=0,
        default='0',
        languageIndependent=1,
        widget=BooleanWidget(label='Show Reset Button',
            label_msgid = "label_showcancel_text",
            description_msgid = "help_showcancel_text",
            i18n_domain = "ploneformgen",
            ),
        ),
    StringField('resetLabel',
        required=0,
        searchable=0,
        default="Reset",
        widget=StringWidget(
                label="Reset Button Label",
                label_msgid = "label_reset_button",
                i18n_domain = 'ploneformgen',
                ),
        ),
    LinesField('actionAdapter',
        vocabulary='actionAdaptersDL',
        widget=MultiSelectionWidget(
            label="Action Adapter",
            description="""
                To make your form do something useful when submitted:
                add one or more form action adapters to the form folder,
                configure them, then return to this
                form and select the active ones.
                """,
            format='checkbox',
            label_msgid = "label_actionadapter_text",
            description_msgid = "help_actionadapter_text",
            i18n_domain = "ploneformgen",
            ),
        ),
    StringField('thanksPage',
        searchable=False,
        required=False,
        vocabulary='thanksPageVocabulary',
        widget=SelectionWidget(
            label='Thanks Page',
            label_msgid = "label_thankspage_text",
            description="""
                Pick a contained page you wish to show on a successful
                form submit. (If none are available, add one.)
                Choose none to simply display the form
                field values.
            """,
            description_msgid = "help_thankspage_text",
            i18n_domain = "ploneformgen",
            ),
        ),
    BooleanField('forceSSL',
        required=False,
        default=False,
        # write_permission=EDIT_ADVANCED_PERMISSION,
        widget=BooleanWidget(
            label='Force SSL connection',
            label_msgid='label_force_ssl',
            description="""
                Check this to make the form redirect to an SSL-enabled
                version of itself (https://) if accessed via a non-SSL
                URL (http://).  In order to function properly,
                this requires a web server that has been configured to
                handle the HTTPS protocol on port 443 and forward it to Zope.
            """,
            description_msgid = 'help_force_ssl',
            i18n_domain = 'ploneformgen',
            ),
        ),
    TextField('formPrologue',
        schemata='decoration',
        required=False,
        # Disable search to bypass a unicode decode error
        # in portal_catalog indexes.
        searchable=False,
        primary=False,
        validators = ('isTidyHtmlWithCleanup', ),
        default_content_type = zconf.ATDocument.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATDocument.allowed_content_types,
        widget = RichWidget(
            label = "Form Prologue",
            label_msgid = "label_prologue_text",
            description = "This text will be displayed above the form fields.",
            description_msgid = "help_prologue_text",
            rows = 8,
            i18n_domain = "ploneformgen",
            allow_file_upload = zconf.ATDocument.allow_document_upload,
            ),
        ),
    TextField('formEpilogue',
        schemata='decoration',
        required=False,
        # Disable search to bypass a unicode decode error
        # in portal_catalog indexes.
        searchable=False,
        primary=False,
        validators = ('isTidyHtmlWithCleanup', ),
        default_content_type = zconf.ATDocument.default_content_type,
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATDocument.allowed_content_types,
        widget = RichWidget(
            label = "Form Epilogue",
            label_msgid = "label_epilogue_text",
            description = "The text will be displayed after the form fields.",
            description_msgid = "help_epilogue_text",
            rows = 8,
            i18n_domain = "ploneformgen",
            allow_file_upload = zconf.ATDocument.allow_document_upload,
            ),
        ),
    StringField('thanksPageOverride',
        schemata='overrides',
        searchable=0,
        required=0,
        languageIndependent=1,
        write_permission=EDIT_TALES_PERMISSION,
        widget=StringWidget(label="Custom Success Action",
            description="""
                Use this field in place of a thanks-page designation
                to determine final action after calling
                your action adapter (if you have one). You would usually use
                this for a custom success template or script.
                Leave empty if unneeded. Otherwise, specify as you would a
                CMFFormController action type and argument,
                complete with type of action to execute
                (e.g., "redirect_to" or "traverse_to")
                and a TALES expression. For example,
                "redirect_to:string:thanks-page" would redirect to
                'thanks-page'.
            """,
            size=70,
            label_msgid = "label_thankspageoverride_text",
            description_msgid = "help_thankspageoverride_text",
            i18n_domain = "ploneformgen",
            ),
        ),
    StringField('formActionOverride',
        schemata='overrides',
        searchable=0,
        required=0,
        write_permission=EDIT_ADVANCED_PERMISSION,
        languageIndependent=1,
        widget=StringWidget(label="Custom Form Action",
            description="""
                Use this field to override the form action attribute.
                Specify a URL to which the form will post.
                This will bypass form validation, success action
                adapter and thanks page.
            """,
            size=70,
            label_msgid = "label_formactionoverride_text",
            description_msgid = "help_formactionoverride_text",
            i18n_domain = "ploneformgen",
            ),
        ),
    TALESString('onDisplayOverride',
        schemata='overrides',
        searchable=0,
        required=0,
        validators=('talesvalidator', ),
        write_permission=EDIT_TALES_PERMISSION,
        default='',
        languageIndependent=1,
        widget=StringWidget(label="Form Setup Script",
            description="""
                A TALES expression that will be called when the form is
                displayed.
                Leave empty if unneeded.
                The most common use of this field is to call a python script
                that sets defaults for multiple fields by pre-populating
                request.form.
                Any value returned by the expression is ignored.
                PLEASE NOTE: errors in the evaluation of this expression
                will cause an error on form display.
            """,
            size=70,
            i18n_domain = "ploneformgen",
            label_msgid = "label_OnDisplayOverride_text",
            description_msgid = "help_OnDisplayOverride_text",
            ),
        ),
    TALESString('afterValidationOverride',
        schemata='overrides',
        searchable=0,
        required=0,
        validators=('talesvalidator', ),
        write_permission=EDIT_TALES_PERMISSION,
        default='',
        languageIndependent=1,
        widget=StringWidget(label="After Validation Script",
            description="""
                A TALES expression that will be called after the form is
                successfully validated, but before calling an action adapter
                (if any) or displaying a thanks page.
                Form input will be in the request.form dictionary.
                Leave empty if unneeded.
                The most common use of this field is to call a python script
                to clean up form input or to script an alternative action.
                Any value returned by the expression is ignored.
                PLEASE NOTE: errors in the evaluation of this expression will
                cause an error on form display.
            """,
            size=70,
            i18n_domain = "ploneformgen",
            label_msgid = "label_AfterValidationOverride_text",
            description_msgid = "help_AfterValidationOverride_text",
            ),
        ),
    TALESString('headerInjection',
        schemata='overrides',
        searchable=0,
        required=0,
        validators=('talesvalidator', ),
        write_permission=EDIT_TALES_PERMISSION,
        default='',
        languageIndependent=1,
        widget=StringWidget(label="Header Injection",
            description="""
                This override field allows you to insert content into the xhtml
                head. The typical use is to add custom CSS or JavaScript.
                Specify a TALES expression returning a string. The string will
                be inserted with no interpretation.
                PLEASE NOTE: errors in the evaluation of this expression will
                cause an error on form display.
            """,
            size=70,
            i18n_domain = "ploneformgen",
            label_msgid = "label_headerInjection_text",
            description_msgid = "help_headerInjection_text",
            ),
        ),
    ))

if HAS_PLONE_PROTECT:
    # Add field for CSRF check option
    FormFolderSchema = FormFolderSchema + Schema((
        BooleanField('checkAuthenticator',
            required=False,
            default=True,
            schemata='overrides',
            write_permission=EDIT_ADVANCED_PERMISSION,
            widget=BooleanWidget(
                label='CSRF Protection',
                label_msgid='label_csrf',
                description="""
                    Check this to employ Cross-Site Request Forgery protection.
                    Note that only HTTP Post actions will be allowed.
                """,
                description_msgid = 'help_csrf',
                i18n_domain = 'ploneformgen',
                ),
            ),
    ))

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

    schema = FormFolderSchema

    content_icon = 'Form.gif'
    meta_type = 'FormFolder'
    portal_type = 'FormFolder'
    archetype_name = 'Form Folder'
    if HAS_PLONE30:
        default_view = immediate_view = 'fg_base_view_p3'
    else:
        default_view = immediate_view = 'fg_base_view'
    suppl_views = ()

    typeDescription = \
        'A folder which creates a form view from contained form fields.'

    security = ClassSecurityInfo()

    security.declarePrivate('_getFieldObjects')

    def _getFieldObjects(self, objTypes=None, includeFSMarkers=False):
        """ return list of enclosed fields """

        # This function currently checks to see if
        # an object is a form field by looking to see
        # if it has an fgField attribute.

        # Make sure we look through fieldsets
        if objTypes is not None:
            objTypes = list(objTypes)[:]
            objTypes.append('FieldsetFolder')

        myObjs = []

        for obj in self.objectValues(objTypes):
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
                if id(object) in cache:
                    del cache[id(object)]

    security.declareProtected(View, 'fgGetFormSubmitAction')

    def fgGetFormSubmitAction(self):
        """ Determines where the form should submit to.

            Tries, in the following order:

              1. The 'pfg_form_action' of the request's "other" vars, which
                 may be set temporarily by the embedded form view.
                 (This is basically a Plone 2.5-compatible version of
                 annotating the request.)

              2. The value of the form's formActionOverride field,
                 which may be set by the manager of the form.

              3. The URL of the form folder.

            The result is converted into an https link if 'force SSL' is on.
        """

        action = self.REQUEST.other.get('pfg_form_action')
        if not action:
            action = getattr(self, 'formActionOverride', None)
        if not action:
            action = self.absolute_url()

        if self.getForceSSL():
            action = action.replace('http://', 'https://')

        return action

    security.declarePrivate('maybeForceSSL')

    def fgMaybeForceSSL(self):
        """ Redirect to an https:// URL if the 'force SSL' option is on.

            However, don't do so for those with rights to edit the form,
            to avoid making the form uneditable if SSL isn't configured
            properly.  These users will still get an SSL-ified form
            action for when the form is submitted.
        """
        if self.getForceSSL() and \
          not getSecurityManager().checkPermission(ModifyPortalContent, self):
            # Make sure we're being accessed via a secure connection
            if self.REQUEST['SERVER_URL'].startswith('http://'):
                secure_url = self.REQUEST['URL'].replace('http://', 'https://')
                raise Redirect(secure_url)

    security.declareProtected(View, 'fgFields')

    def fgFields(self, request=None, displayOnly=False,
                 excludeServerSide=True):
        """ generate fields on the fly; also primes request with
            defaults if request is passed.
            if displayOnly, label fields are excluded.
        """

        self.fgMaybeForceSSL()

        if request and self.getRawOnDisplayOverride():
            # call the tales expression, passing a custom context
            self.getOnDisplayOverride()
            self.cleanExpressionContext(request=request)

        myFields = []
        for obj in self._getFieldObjects(includeFSMarkers=not displayOnly):
            if implementedOrProvidedBy(IField, obj):
                # this is a field -- not a form field -- and may be
                # added directly to the field list.
                if not displayOnly:
                    myFields.append(obj)
            else:
                if request:
                    # prime the request
                    obj.fgPrimeDefaults(request)

                if not (displayOnly and obj.isLabel()) and \
                   not (excludeServerSide and obj.getServerSide()):
                    myFields.append(obj.fgField)

        return myFields

    security.declareProtected(View, 'fgvalidate')

    def fgvalidate(self,
                   REQUEST=None,
                   errors=None,
                   data=None,
                   metadata=None,
                   skip_action_adapters=False):
        """Validates the field data from the request.
        """

        if HAS_PLONE30 and getattr(self, 'checkAuthenticator', True):
            # CSRF check.
            plone.protect.CheckAuthenticator(REQUEST)
            plone.protect.PostOnly(REQUEST)

        _marker = []
        if errors is None:
            errors = {}
        if errors:
            return errors

        # Get all the form fields. Exclude actual IField fields.
        fields = [fo for fo in self._getFieldObjects()
                  if not implementedOrProvidedBy(IField, fo)]
        for obj in fields:
            field = obj.fgField

            if obj.getServerSide():
                # for server-side only fields, use the default value
                # even if something was in the request
                if obj.__name__ in REQUEST.form:
                    del REQUEST.form[obj.__name__]
                obj.fgPrimeDefaults(REQUEST)
            result = field.widget.process_form(self, field, REQUEST.form,
                                               empty_marker=_marker)

            if result is None or result is _marker:
                #XXX Make this smarter
                value = ''
            else:
                value = result[0]

            # workaround what I consider a Zope marshalling error:
            # the production of lists like ['one', ''] and ['']
            # for list fields. No need to worry about polymorphism here,
            # as this is a very particular case.
            if isinstance(value, type([])) and len(value) and \
              (type(value[-1]) in StringTypes) and (len(value[-1]) == 0):
                value.pop()

            # eliminate trailing white space in string types.
            if safe_hasattr(value, 'rstrip'):
                newvalue = value.rstrip()
                if newvalue != value:
                    value = newvalue
                    # since strings are immutable,
                    # we have to manually store it back to the request
                    if safe_hasattr(REQUEST, 'form'):
                        REQUEST.form[obj.getFieldFormName()] = value

            # Archetypes field validation
            res = field.validate(instance=self, value=value, errors=errors,
                                 REQUEST=REQUEST)

            if not res:
                # give the field itself an opportunity to validate.
                res = obj.specialValidator(value, field, REQUEST, errors)

            if res:
                errors[field.getName()] = \
                  validationMessages.cleanupMessage(res, self.REQUEST, self)
            elif shasattr(obj, 'getFgTValidator') and obj.getRawFgTValidator():
                # process the override validator TALES expression

                # create a context for expression evaluation
                context = getExprContext(self, obj)

                # put this field's input (from request)
                # into the context globals as 'value'
                context.setGlobal('value',
                                  REQUEST.form.get(obj.getFieldFormName(),
                                  None))

                # call the tales expression, passing our custom context
                cerr = obj.getFgTValidator(expression_context=context)
                if cerr:
                    errors[field.getName()] = cerr

        if not skip_action_adapters:
            return self.fgProcessActionAdapters(errors, fields, REQUEST)

        return errors

    def fgProcessActionAdapters(self, errors, fields=None, REQUEST=None):
        if fields is None:
            fields = [fo for fo in self._getFieldObjects()
                      if not implementedOrProvidedBy(IField, fo)]

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
                    logger.warn(
                      "Designated action adapter '%s' is missing; ignored." %
                      adapter)
                else:
                    # Now, see if we should execute it.
                    # Check to see if execCondition exists and has contents
                    if safe_hasattr(actionAdapter, 'execCondition') and \
                      len(actionAdapter.getRawExecCondition()):
                        # evaluate the execCondition.
                        # create a context for expression evaluation
                        context = getExprContext(self, actionAdapter)
                        doit = actionAdapter.getExecCondition(
                          expression_context=context)
                    else:
                        # no reason not to go ahead
                        doit = True

                    if doit:
                        result = actionAdapter.onSuccess(fields, \
                                                         REQUEST=REQUEST)
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

        target = 'fg_result_view'

        if safe_hasattr(self, 'thanksPageOverride'):
            s = self.getThanksPageOverride()
            if s:
                return s

        s = getattr(self, 'thanksPage', None)
        if s:
            obj = getattr(self, s, None)
            if obj:
                target = obj.getId()

        is_embedded = self.REQUEST.form.get('pfg_form_marker', False)
        if is_embedded:
            # Change the request URL and then raise a Retry exception
            # so the traversed page renders using the same request
            path = self.REQUEST._orig_env.get('PATH_TRANSLATED', '/')
            try:
                path = path[:path.index('VirtualHostRoot') + 15] + '/'
            except ValueError:
                path = '/'
            path = path + '/'.join(
              self.REQUEST.physicalPathToVirtualPath(self.getPhysicalPath())) \
              + '/' + target
            self.REQUEST._orig_env['PATH_INFO'] = \
              self.REQUEST._orig_env['PATH_TRANSLATED'] = path
            self.REQUEST._orig_env['X_PFG_RETRY'] = '1'
            # commit current transaction since raising Retry would abort it
            transaction.commit()
            raise Retry
        else:
            # if not embedded, simple CMFFormController
            # traversal will work fine
            return 'traverse_to:string:%s' % target

    def getRawActionAdapter(self):
        """ Returns selected action adapters as tuple """

        # this method translates a string actionAdapter
        # attribute from a previous version into a tuple
        try:
            self.actionAdapter + ''
            if self.actionAdapter:
                return (self.actionAdapter, )
            else:
                return ()
        except:
            return self.actionAdapter


    security.declareProtected(ModifyPortalContent, 'actionAdaptersDL')

    def actionAdaptersDL(self):
        """ returns Display List (id, title) tuples of contained adapters """

        # an adapter provides IPloneFormGenActionAdapter
        allAdapters = [(obj.getId(), obj.title) for obj in self.objectValues()
          if implementedOrProvidedBy(IPloneFormGenActionAdapter, obj)]

        if allAdapters:
            return DisplayList(allAdapters)

        return DisplayList()


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
            myFields.append((noneValue, _(u'vocabulary_none_text', u'None')))

        for obj in self._getFieldObjects(objTypes):
            if obj.getServerSide():
                continue
            if isinstance(obj.title, unicode):
                myFields.append((obj.getId(), obj.title))
            else:
                myFields.append((obj.getId(),
                                 obj.title.decode(self.getCharset())))

        return DisplayList(myFields)


    security.declareProtected(ModifyPortalContent, 'thanksPageVocabulary')

    def thanksPageVocabulary(self):
        """ returns a DisplayList of contained page-ish documents """

        propsTool = getToolByName(self, 'portal_properties')
        siteProperties = getattr(propsTool, 'site_properties')
        defaultPageTypes = siteProperties.getProperty('default_page_types')

        tpages = [('', _(u'vocabulary_none_text', u'None')), ]

        for obj in self.objectValues():
            if implementedOrProvidedBy(IPloneFormGenThanksPage, obj) or \
              getattr(obj.aq_explicit, 'portal_type', 'none') in defaultPageTypes:
                tpages.append((obj.getId(), obj.title))

        return DisplayList(tpages)


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
            uid_catalog.uncatalog_object(getRelURL(self, obj.getPhysicalPath()))

        else:
            obj.reindexObject()

    def initializeArchetype(self, **kwargs):
        """ Create sample content that may help folks
            figure out how this gadget works.
        """

        ATFolder.initializeArchetype(self, **kwargs)

        self.setSubmitLabel(zope.i18n.translate(_(u'pfg_formfolder_submit', u'Submit'), context=self.REQUEST))
        self.setResetLabel(zope.i18n.translate(_(u'pfg_formfolder_reset', u'Reset'), context=self.REQUEST))

        oids = self.objectIds()

        # if we have *any* content already, we don't need
        # the sample content
        if not oids:

            haveMailer = False
            # create a mail action
            try:
                self.invokeFactory('FormMailerAdapter', 'mailer')
                mailer = self['mailer']

                mailer.setTitle(zope.i18n.translate(
                  _(u'pfg_mailer_title', u'Mailer'),
                  context=self.REQUEST))
                mailer.setDescription(
                  zope.i18n.translate(
                    _(u'pfg_mailer_description',
                      u'E-Mails Form Input'),
                    context=self.REQUEST))

                self._pfFixup(mailer)

                self.actionAdapter = ('mailer', )
                haveMailer = True
            except Unauthorized:
                logger.warn('User not authorized to create mail adapters. Form Folder created with no action adapter.')

            # create a replyto field
            self.invokeFactory('FormStringField', 'replyto')
            obj = self['replyto']
            obj.fgField.__name__ = 'replyto'

            obj.setTitle(zope.i18n.translate(
              _(u'pfg_replytofield_title', u'Your E-Mail Address'),
              context=self.REQUEST))

            obj.fgField.required = True
            obj.setFgStringValidator('isEmail')
            obj.setFgTDefault('here/memberEmail')
            obj.setFgDefault('dynamically overridden')

            self._pfFixup(obj)

            if haveMailer:
                mailer.replyto_field = 'replyto'

            # create a subject field
            self.invokeFactory('FormStringField', 'topic')
            obj = self['topic']
            obj.fgField.__name__ = 'topic'

            obj.setTitle(zope.i18n.translate(
              _(u'pfg_topicfield_title', u'Subject'),
              context=self.REQUEST))

            obj.fgField.required = True

            self._pfFixup(obj)

            if haveMailer:
                mailer.subject_field = 'topic'

            # create a comments field
            self.invokeFactory('FormTextField', 'comments')
            obj = self['comments']
            obj.fgField.__name__ = 'comments'

            obj.setTitle(zope.i18n.translate(
              _(u'pfg_commentsfield_title', u'Comments'),
              context=self.REQUEST))

            obj.fgField.required = True

            self._pfFixup(obj)


            # create a thanks page
            self.invokeFactory('FormThanksPage', 'thank-you')
            obj = self['thank-you']

            obj.setTitle(zope.i18n.translate(
              _(u'pfg_thankyou_title', u'Thank You'), context=self.REQUEST))
            obj.setDescription(zope.i18n.translate(
              _(u'pfg_thankyou_description', u'Thanks for your input.'),
              context=self.REQUEST))

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


    security.declareProtected(ModifyPortalContent, 'setFormPrologue')

    def toggleActionActive(self, item_id, **kw):
        """ toggle the active status of an action adapter """

        work = list(self.actionAdapter)
        if item_id in work:
            work.remove(item_id)
        else:
            work.append(item_id)
        self.actionAdapter = work
        return "<done />"

    security.declareProtected(ModifyPortalContent, 'setThanksPage')

    def setThanksPage(self, value, *kw):
        """ Set the thanks page """

        self.thanksPage = value
        return "<done />"


    security.declareProtected(ModifyPortalContent, 'reorderField')

    def reorderField(self, item_id, target_id, **kw):
        """ move item to target"""

        itemPos = self.getObjectPosition(item_id)
        targetPos = self.getObjectPosition(target_id)

        self.moveObjectsByDelta(item_id, targetPos-itemPos)
        self.plone_utils.reindexOnReorder(self)

        return "<done />"

registerATCT(FormFolder, PROJECTNAME)

#    security.declareProtected(ModifyPortalContent, 'myi18n')
#    def myi18n(self):
#        """ return i18n declarations from widgets """
#
#        boilerplate = """\n#. %s\n#. Default: "%s"\nmsgid "%s"\nmsgstr ""\n"""
#
#        res = ''
#
#        from Products.PloneFormGen.content.fields import *
#        from Products.PloneFormGen.content.formMailerAdapter import *
#        from Products.PloneFormGen.content.saveDataAdapter import *
#        from Products.PloneFormGen.content.thanksPage import *
#
#
#        klasses = (
#            FormFolder,
#            FGStringField,
#            FGPasswordField,
#            FGIntegerField,
#            FGFixedPointField,
#            FGBooleanField,
#            FGDateField,
#            FGLabelField,
#            FGLinesField,
#            FGSelectionField,
#            FGMultiSelectField,
#            FGTextField,
#            FGRichTextField,
#            FGFileField,
#            FormMailerAdapter,
#            FormSaveDataAdapter,
#            FormThanksPage,
#            )
#
#        done = {}
#
#        for myclass in klasses:
#            myname = myclass.archetype_name
#            myschema = myclass.schema
#
#            # res = res + "\n### %s ###\n" % myname
#
#            for aschema in myschema.getSchemataNames():
#                for field in myschema.getSchemataFields(aschema):
#                    widget = field.widget
#                    domain = getattr(widget, 'i18n_domain', None)
#
#                    if domain == 'ploneformgen':
#
#
#                        id = getattr(widget, 'label_msgid', '***NO label_msgid***')
#                        val = widget.label
#                        if done.get(id) != val:
#                            msg = boilerplate % (myname, val, id)
#                            res = "%s%s\n" % (res, msg)
#                            done[id] = val
#                        #else:
#                        #    res = res + "\navoided repeating %s for %s" % (id, myname)
#
#                        desc = widget.description
#                        if desc:
#                            desid = getattr(widget, 'description_msgid', '***NO description_msgid***')
#                            if done.get(desid) != desc:
#                                mdesc = "\n#. Default: ".join( [ln.strip() for ln in desc.split('\n')] )
#                                msg = boilerplate % (myname, mdesc, desid)
#                                done[desid] = desc
#                                res = "%s%s\n" % (res, msg)
#                            #else:
#                            #    res = res + "\navoided repeating %s for %s" % (desid, myname)
#
#                    elif domain not in ('plone', 'atcontenttypes',):
#                        res = "%s\n***Unexpected domain for %s:%s: %s\n" % (res, myname, widget.label, domain)
#
#        return res
