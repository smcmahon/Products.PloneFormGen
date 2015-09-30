""" Base declarations and classes for form fields """

__author__ = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

import cgi

from types import StringTypes, BooleanType

import transaction
import zExceptions

from zope.interface import implements

from Products.Archetypes.public import *
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.configuration import zconf

from Products.TALESField import TALESString, TALESLines

from Products.PloneFormGen.config import \
    PROJECTNAME, EDIT_TALES_PERMISSION, EDIT_ADVANCED_PERMISSION

from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.exceptions import BadRequest
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.utils import base_hasattr, safe_hasattr, safe_unicode

from Products.validation.validators import RangeValidator
from AccessControl import ClassSecurityInfo

from Products.PloneFormGen.content import validationMessages
from Products.PloneFormGen.interfaces import IPloneFormGenField

from Products.PloneFormGen import PloneFormGenMessageFactory as _


def finalizeFieldSchema(schema, folderish=True, moveDiscussion=False):
    """ cleanup typical field schema """

    finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
    # avoid showing unnecessary schema tabs
    for afield in ('subject',
                   'relatedItems',
                   'location',
                   'language',
                   'effectiveDate',
                   'expirationDate',
                   'creation_date',
                   'modification_date',
                   'creators',
                   'contributors',
                   'rights',
                   'allowDiscussion',
                   'excludeFromNav',):
        schema[afield].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
        schema[afield].schemata = 'default'


###
# we use these fields in several schemata

validatorOverrideField = \
        TALESString('fgTValidator',
            schemata='overrides',
            searchable=0,
            required=0,
            validators=('talesvalidator',),
            default="python:False",
            write_permission=EDIT_TALES_PERMISSION,
            widget=StringWidget(label=_(u'label_fgtvalidator_text', default=u"Custom Validator"),
                description=_(u'help_fgtvalidator_text', default=\
                    u"A TALES expression that will be evaluated when the form is validated."
                    "Validate against 'value', which will contain the field input."
                    "Return False if valid; if not valid return a string error message."
                    "E.G., \"python: test(value=='eggs', False, 'input must be eggs')\" will"
                    "require \"eggs\" for input."
                    "PLEASE NOTE: errors in the evaluation of this expression will cause"
                    "an error on form display."),
                size=70,
                ),
            )

rowsField = \
    IntegerField('fgRows',
        searchable=0,
        required=0,
        default='5',
        widget=IntegerWidget(label=_(u'label_rows_text', default=u'Rows'),
            description=_(u'help_rows_text', default=u''),
            ),
        )

maxlengthField = \
    IntegerField('fgmaxlength',
        default=255,
        widget=IntegerWidget(
            label=_(u'label_fgmaxlength_text', default=u'Max Length'),
            description=_(u'help_fgmaxlength_text', default=u"The maximum "
                "number of characters the user will be able to input."
                "Use 0 for no limit."),
            ),
        )

maxlengthField0 = \
        IntegerField('fgmaxlength',
            default=0,
            widget=IntegerWidget(
                label=_(u'label_fgmaxlength_text', default=u'Max Length'),
                description=_(u'help_fgmaxlength_text', default=u"The maximum "
                    "number of characters the user will be able to input."
                    "Use 0 for no limit."),
                ),
            )

maxlengthField4k = \
        IntegerField('fgmaxlength',
            default='4096',
            widget=IntegerWidget(
                label=_(u'label_fgmaxlength_text', default=u'Max Length'),
                description=_(u'help_fgmaxlength_text', default=u"The maximum "
                    "number of characters the user will be able to input."
                    "Use 0 for no limit."),
                ),
            )

sizeField = \
    IntegerField('fgsize',
        default=30,
        widget=IntegerWidget(
            label=_(u'label_fgsize_text', default=u'Size'),
            description=_(u'help_fgsize_text', default=u'The size of the text-entry box, in characters.'),
            ),
        )

vocabularyField = \
    LinesField('fgVocabulary',
        searchable=0,
        required=0,
        widget=LinesWidget(label=_(u'label_fgvocabulary_text',
                                   default=u'Options'),
            description=_(u'help_fgvocabulary_text', default=u"""
                Use one line per option.
                Note that this may be overridden dynamically.
                [Note, you may optionally use a "value|label" format.]
                """),
            ),
        )

vocabularyOverrideField = \
    TALESString('fgTVocabulary',
        schemata='overrides',
        searchable=0,
        required=0,
        validators=('talesvalidator',),
        default='',
        write_permission=EDIT_TALES_PERMISSION,
        widget=StringWidget(label=_(u'label_fgtvocabulary_text',
                                    default=u"Options Vocabulary"),
            description=_(u'help_fgtvocabulary_text', default=u"""
                A TALES expression that will be evaluated when the form is displayed
                to get the field options.
                Leave empty if unneeded.
                Your TALES expression should evaluate as a list of (key, value) tuples.
                PLEASE NOTE: errors in the evaluation of this expression will cause
                an error on form display.
            """),
            size=70,
            ),
        )

# establish a bare baseline
# only label field uses this without change
BareFieldSchema = ATContentTypeSchema.copy()
BareFieldSchema['title'].searchable = False
BareFieldSchema['title'].widget.label = _(u'label_fieldlabel_text', default=u'Field Label')
BareFieldSchema['description'].searchable = False
BareFieldSchema['description'].widget.label = _(u'label_fieldhelp_text', default=u'Field Help')
BareFieldSchema['description'].widget.description = None

###
# BaseFieldSchema -- more common baseline
# Used as a base schema for several fields

BaseFieldSchema = BareFieldSchema.copy() + Schema((
        BooleanField('required',
            searchable=0,
            required=0,
            widget=BooleanWidget(
                label=_(u'label_required_text', default=u"Required"),
                ),
            ),
        BooleanField('hidden',
            searchable=0,
            required=0,
            write_permission=EDIT_ADVANCED_PERMISSION,
            widget=BooleanWidget(
                label=_(u'label_hidden_text', default=u"Hidden"),
                ),
            ),
        TALESString('fgTDefault',
            schemata='overrides',
            searchable=0,
            required=0,
            validators=('talesvalidator',),
            write_permission=EDIT_TALES_PERMISSION,
            default='',
            widget=StringWidget(label=_(u'label_fgtdefault_text',
                                        default=u"Default Expression"),
                description=_(u'help_fgtdefault_text', default=u"""
                    A TALES expression that will be evaluated when the form is displayed
                    to get the field default value.
                    Leave empty if unneeded. Your expression should evaluate as a string.
                    PLEASE NOTE: errors in the evaluation of this expression will cause
                    an error on form display.
                """),
                size=70,
                ),
            ),
        validatorOverrideField,
        TALESString('fgTEnabled',
            schemata='overrides',
            searchable=0,
            required=0,
            validators=('talesvalidator',),
            write_permission=EDIT_TALES_PERMISSION,
            default='',
            widget=StringWidget(label=_(u'label_fgtenable_text', default=u"Enabling Expression"),
                description=_(u'help_fgtenable_text', default=\
                    u"A TALES expression that will be evaluated when the form is displayed"
                    "to determine whether or not the field is enabled."
                    "Your expression should evaluate as True if"
                    "the field should be included in the form, False if it should be omitted."
                    "Leave this expression field empty if unneeded: the field will be included."
                    "PLEASE NOTE: errors in the evaluation of this expression will cause"
                    "an error on form display."),
                size=70,
                ),
            ),
        BooleanField('serverSide',
            schemata='overrides',
            searchable=0,
            required=0,
            write_permission=EDIT_ADVANCED_PERMISSION,
            default='',
            widget=BooleanWidget(
                label=_(u'label_server_side_text', default=u"Server-Side Variable"),
                description=_(u'description_server_side_text', default=\
                    u"Mark this field as a value to be injected into the"
                    "request form for use by action adapters and is not"
                    "modifiable by or exposed to the client."),
                ),
            ),
        StringField('placeholder',
            searchable=0,
            required=0,
            widget=StringWidget(
                label=_(u'label_placeholder', default=u'Placeholder'),
                description=_(u'help_placeholder', default=u"A placeholder for text input fields."),
            ),
        ),
    ))


##
# BaseFieldSchemaStringDefault
# A base schema for fields that have a string default

BaseFieldSchemaStringDefault = BaseFieldSchema.copy() + Schema((
        StringField('fgDefault',
            searchable=0,
            required=0,
            widget=StringWidget(label=_(u'label_fgdefault_text', default=u'Default'),
            description=_(u'help_fgdefault_text', default=u"The value the field "
                "should contain when the form is first displayed."
                "Note that this may be overridden dynamically."),
            ),
        ),
    ))


##
# BaseFieldSchemaLinesDefault
# A base schema for fields that have a lines default

BaseFieldSchemaLinesDefault = BaseFieldSchema.copy() + Schema((
        LinesField('fgDefault',
            searchable=0,
            required=0,
            widget=LinesWidget(label=_(u'label_fglinesdefault_text', default=u'Default'),
                description=_(u'help_fglinesdefault_text', default=u"""
                    The values the field should contain when the form is first displayed.
                    Use one value per line.
                    Note that this may be overridden dynamically.
                """),
                ),
            ),
        rowsField,
        TALESString('fgTDefault',
            schemata='overrides',
            searchable=0,
            required=0,
            validators=('talesvalidator',),
            default='',
            write_permission=EDIT_TALES_PERMISSION,
            widget=StringWidget(label=_(u'label_fgtlinesdefault_text', default=u"Default Expression"),
                description=_(u'help_fgtlinesdefault_text', default=u"""
                    A TALES expression that will be evaluated when the form is displayed
                    to get the field default value.
                    Leave empty if unneeded. Your expression should evaluate as a list or tuple.
                    PLEASE NOTE: errors in the evaluation of this expression will cause
                    an error on form display.
                """),
                size=70,
                ),
            ),
        validatorOverrideField,
    ))


##
# BaseFieldSchemaTextDefault
# A base schema for fields that have a textarea default

BaseFieldSchemaTextDefault = BaseFieldSchema.copy() + Schema((
        TextField('fgDefault',
            searchable=0,
            required=0,
            widget=TextAreaWidget(label=_(u'label_fgtextdefault_text', default=u'Default'),
                description=_(u'help_fgtextdefault_text', default=u"""
                    The text the field should contain when the form is first displayed.
                    Note that this may be overridden dynamically.
                """),
                ),
            ),
        rowsField,
        maxlengthField0,
        TALESString('fgTDefault',
            schemata='overrides',
            searchable=0,
            required=0,
            validators=('talesvalidator',),
            default='',
            write_permission=EDIT_TALES_PERMISSION,
            widget=StringWidget(label=_(u'label_fgtdefault_text', default=u"Default Expression"),
                description=_(u'help_fgtdefault_text', default=u"""
                    A TALES expression that will be evaluated when the form is displayed
                    to get the field default value.
                    Leave empty if unneeded. Your expression should evaluate as a string.
                    PLEASE NOTE: errors in the evaluation of this expression will cause
                    an error on form display.
                """),
                size=70,
            ),
        ),
        validatorOverrideField,
    ))

##
# BaseFieldSchemaRichTextDefault
# A base schema for fields that have a rich editor default

BaseFieldSchemaRichTextDefault = BaseFieldSchema.copy() + Schema((
        TextField('fgDefault',
            searchable=0,
            required=0,
            validators=('isTidyHtmlWithCleanup',),
            default_content_type='text/html',
            default_output_type='text/x-html-safe',
            allowable_content_types=zconf.ATDocument.allowed_content_types,
            widget=TinyMCEWidget(label=_(u'label_fgtextdefault_text', default=u'Default'),
                description=_(u'help_fgtextdefault_text', default=u"""
                    The text the field should contain when the form is first displayed.
                    Note that this may be overridden dynamically.
                """),
                allow_file_upload=False,
                ),
            ),
        rowsField,
        maxlengthField4k,
        TALESString('fgTDefault',
            schemata='overrides',
            searchable=0,
            required=0,
            validators=('talesvalidator',),
            default='',
            write_permission=EDIT_TALES_PERMISSION,
            widget=StringWidget(label=_(u'label_fgtdefault_text', default=u"Default Expression"),
                description=_(u'help_fgtdefault_text', default=u"""
                    A TALES expression that will be evaluated when the form is displayed
                    to get the field default value.
                    Leave empty if unneeded. Your expression should evaluate as a string.
                    PLEASE NOTE: errors in the evaluation of this expression will cause
                    an error on form display.
                """),
                size=70,
            ),
        ),
        validatorOverrideField,
    ))

finalizeFieldSchema(BareFieldSchema, folderish=True, moveDiscussion=False)
finalizeFieldSchema(BaseFieldSchema, folderish=True, moveDiscussion=False)
finalizeFieldSchema(BaseFieldSchemaStringDefault, folderish=True, moveDiscussion=False)
finalizeFieldSchema(BaseFieldSchemaLinesDefault, folderish=True, moveDiscussion=False)
finalizeFieldSchema(BaseFieldSchemaTextDefault, folderish=True, moveDiscussion=False)
finalizeFieldSchema(BaseFieldSchemaRichTextDefault, folderish=True, moveDiscussion=False)


class StringVocabularyField(StringField):
    """
    Parent for fields that have vocabularies.
    Overrides Vocabulary so that we can get the value from the instance
    """

    security = ClassSecurityInfo()

    security.declarePublic('Vocabulary')
    def Vocabulary(self, content_instance=None):
        """
        Returns a DisplayList.
        """
        # if there's a TALES override, return it as a DisplayList,
        # otherwise, build the DisplayList from fgVocabulary

        fieldContainer = content_instance.findFieldObjectByName(self.__name__)

        vl = fieldContainer.getFgTVocabulary()
        if vl is not None:
            return DisplayList(data=vl)

        res = DisplayList()
        for line in fieldContainer.fgVocabulary:
            lsplit = line.split('|')
            if len(lsplit) == 2:
                key, val = lsplit
            else:
                key, val = (lsplit[0], lsplit[0])
            res.add(key, val)
        return res


class LinesVocabularyField(StringField):
    """ Same as StringVocabularyField, but based on a LinesField """

    security = ClassSecurityInfo()

    security.declarePublic('Vocabulary')
    def Vocabulary(self, content_instance=None):
        """
        Returns a DisplayList.
        """
        # if there's a TALES override, return it as a DisplayList,
        # otherwise, build the DisplayList from fgVocabulary

        fieldContainer = content_instance.findFieldObjectByName(self.__name__)

        vl = fieldContainer.getFgTVocabulary()
        if vl is not None:
            return DisplayList(data=vl)

        res = DisplayList()
        for line in fieldContainer.fgVocabulary:
            lsplit = line.split('|')
            if len(lsplit) == 2:
                key, val = lsplit
            else:
                key, val = (lsplit[0], lsplit[0])
            res.add(key, val)
        return res

NO_TRAVERSE = (
    'fgTValidator',
    'fgTVocabulary',
    'fgTDefault',
    'fgTEnabled',
    'fgTDefault',
    'fgDefault',
    'fgTDefault',
    'fgDefault',
    'fgTDefault',
    )


class BaseFormField(ATCTContent):
    """
    Base form generator form field class.
    Provides several methods useful to descendents.
    """
    implements(IPloneFormGenField)

    security = ClassSecurityInfo()

    schema = BaseFieldSchema

    # Standard content type setup
    portal_type = meta_type = 'BaseFormField'
    archetype_name = 'Base Form Field'
    content_icon = 'BasicField.gif'
    typeDescription = 'A form field'

    default_view = immediate_view = 'fg_base_view_p3'
    suppl_views = ()

    # Let's not pollute the global "add"
    global_allow = 0

    def __bobo_traverse__(self, REQUEST, name):
        # prevent traversal to attributes we want to protect
        if name in NO_TRAVERSE:
            print name
            raise AttributeError
        return super(BaseFormField, self).__bobo_traverse__(REQUEST, name)


    security.declareProtected(ModifyPortalContent, 'setDescription')
    def setDescription(self, value, **kw):
        """ set description for field widget """

        self.fgField.widget.description = value
        self.getField('description').set(self, value, **kw)


    security.declareProtected(ModifyPortalContent, 'setPlaceholder')
    def setPlaceholder(self, value, **kw):
        """ set placeholder for field widget """

        self.fgField.widget.placeholder = value


    security.declareProtected(View, 'getPlaceholder')
    def getPlaceholder(self, **kw):
        """ get placeholder for field widget """
        return getattr(self.fgField.widget, 'placeholder', None)


    security.declareProtected(ModifyPortalContent, 'setRequired')
    def setRequired(self, value, **kw):
        """ set required flag for field """

        if type(value) == BooleanType:
            self.fgField.required = value
        else:
            self.fgField.required = value == '1' or value == 'True'


    security.declareProtected(View, 'getRequired')
    def getRequired(self, **kw):
        """ get required flag for field """

        return self.fgField.required


    security.declareProtected(ModifyPortalContent, 'setHidden')
    def setHidden(self, value, **kw):
        """ set hidden flag for field widget """

        if type(value) == BooleanType:
            if value:
                self.fgField.widget.visible = -1
            else:
                self.fgField.widget.visible = 1
        elif value == '1' or value == 'True':
            self.fgField.widget.visible = -1
        else:
            self.fgField.widget.visible = 1


    security.declareProtected(View, 'getHidden')
    def getHidden(self, **kw):
        """ get hidden flag for field widget """

        return self.fgField.widget.visible == -1

    security.declareProtected(View, 'getServerSide')
    def getServerSide(self, **kw):
        """ return server side flag for field """
        try:
            return self.getField('serverSide').get(self)
        except AttributeError:
            return False

    security.declareProtected(ModifyPortalContent, 'setTitle')
    def setTitle(self, value, **kw):
        """ set title of object and field label """

        self.title = value
        if isinstance(value, unicode):
            uvalue = value
        else:
            charset = 'utf-8'
            uvalue = unicode(value, charset)
        self.fgField.widget.label = uvalue


    security.declareProtected(ModifyPortalContent, 'setId')
    def setId(self, value):
        """Sets the object id. Changes both object and field id.
        """

        badIds = (
            'language',
            'form',
            'form_submit',
            'fieldset',
            'last_referer',
            'add_reference',
            )

        if value in badIds:
            raise BadRequest, 'The id "%s" is reserved.' % value

        BaseContent.setId(self, value)
        self.fgField.__name__ = self.getId()


    security.declareProtected(ModifyPortalContent, 'setFgmaxlength')
    def setFgmaxlength(self, value, **kw):
        """ set maxlength for field widget """

        if value == '0':
            self.fgField.widget.maxlength = False
        else:
            self.fgField.widget.maxlength = value


    security.declareProtected(View, 'getFgmaxlength')
    def getFgmaxlength(self, **kw):
        """ get maxlength for field widget """

        ml = self.fgField.widget.maxlength
        if ml:
            return ml
        else:
            return '0'


    security.declareProtected(ModifyPortalContent, 'setFgsize')
    def setFgsize(self, value, **kw):
        """ set size for field widget """

        self.fgField.widget.size = value


    security.declareProtected(View, 'getFgsize')
    def getFgsize(self, **kw):
        """ get size for field widget """

        return self.fgField.widget.size

    security.declareProtected(ModifyPortalContent, 'setFgRows')
    def setFgRows(self, value, **kw):
        """ sets widget rows """

        self.fgField.widget.rows = value


    security.declareProtected(View, 'getFgRows')
    def getFgRows(self, **kw):
        """ gets widget rows """

        return self.fgField.widget.rows


# style sheet sets visual column widths
#    security.declareProtected(View, 'setFgCols')
#    def setFgCols(self, value, **kw):
#        """ sets widget columns """
#
#        self.fgField.widget.cols = value
#
#
#    security.declareProtected(View, 'getFgCols')
#    def getFgCols(self, **kw):
#        """ Sets widget columns """
#
#        return self.fgField.widget.cols


    security.declareProtected(View, 'getMinval')
    def getMinval(self, **kw):
        """ get minval for field """

        return self.fgField.minval


    security.declareProtected(ModifyPortalContent, 'setMinval')
    def setMinval(self, value, **kw):
        """ set minval for field """

        self.fgField.minval = value


    security.declareProtected(View, 'getMaxval')
    def getMaxval(self, **kw):
        """ get maxval for field """

        return self.fgField.maxval


    security.declareProtected(ModifyPortalContent, 'setMaxval')
    def setMaxval(self, value, **kw):
        """ set maxaxval for field """

        self.fgField.maxval = value


    security.declareProtected(ModifyPortalContent, 'setFgStringValidator')
    def setFgStringValidator(self, value, **kw):
        """ set simple validator """

        if value:
            self.fgField.validators = ('isNotTooLong', value)
        else:
            self.fgField.validators = ('isNotTooLong',)
        self.fgField._validationLayer()

        self.fgStringValidator = value


    security.declareProtected(View, 'fgPrimeDefaults')
    def fgPrimeDefaults(self, request, contextObject=None):
        """ primes request with default """

        # the field macros will try to get the field value
        # via Field.getEditAccessor. Unfortunately, it looks for it
        # as an attribute of the object, not the field.
        # so, communicate via the request, but don't overwrite
        # what's already there.

        if safe_hasattr(self, 'getFgTDefault') and self.getRawFgTDefault():
            if contextObject:
                # see note in fgvalidate
                value = self.getFgTDefault(expression_context=getExprContext(self, contextObject))
            else:
                value = self.getFgTDefault()
        else:
            value = None

        if (value is None) and safe_hasattr(self, 'getFgDefault'):
            value = self.getFgDefault()
        if value:
            request.form.setdefault(self.fgField.__name__, value)


    security.declareProtected(View, 'fgFields')
    def fgFields(self, request=None):
        """ generate fields on the fly; also primes request with defaults """

        if request:
            self.fgPrimeDefaults(request)

        return (self.fgField,)


    security.declarePrivate('_specialValidator')
    def specialValidator(self, value, field, REQUEST, errors):
        """
        Override this method to provide a custom field validator.
        It will be called before other validators.
        As with Archetypes validators, return 0 if value is OK,
        a string error message if invalid.
        If invalid, no other validators will be run for this field.
        """

        return 0


    security.declareProtected(View, 'fgvalidate')
    def fgvalidate(self, REQUEST=None, errors=None, data=None, metadata=None):
        # Validates the field data from the request.

        _marker = []
        if errors is None:
            errors = {}
        if errors:
            return errors

        field = self.fgField

        result = field.widget.process_form(self, field, REQUEST.form, empty_marker=_marker)

        if result is None or result is _marker:
            #XXX Make this smarter
            value = ''
        else:
            value = result[0]

        # workaround what I consider a Zope marshalling error: the production
        # of lists like ['one', ''] and [''].
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
                    REQUEST.form[self.getFieldFormName()] = value

        # Archetypes field validation
        res = field.validate(instance=self,
                            value=value,
                            errors=errors,
                            REQUEST=REQUEST)

        if not res:
            # give the field itself an opportunity to validate.
            res = self.specialValidator(value, field, REQUEST, errors)

        if res:
            errors[field.getName()] = validationMessages.cleanupMessage(res, self.REQUEST, self)
        elif safe_hasattr(self, 'getFgTValidator') and self.getRawFgTValidator():
            # process the override validator TALES expression

            # create a context for expression evaluation.
            # Note that we're explicitly passing the form object to getExprContext;
            # this makes sure we don't cache the wrong context.
            context = getExprContext(self, self.aq_parent)

            # put this field's input (from request) into the context globals
            # as 'value'
            context.setGlobal('value', REQUEST.form.get(self.getFieldFormName(), None))

            # call the tales expression, passing our custom context
            cerr = self.getFgTValidator(expression_context=context)
            if cerr:
                errors[field.getName()] = cerr

        return errors


    security.declareProtected(View, 'fgGetSuccessAction')
    def fgGetSuccessAction(self):
        # """
        #      Returns string id of success action template or script.
        #      Controller will traverse to this on successful validation.
        # """

        return 'traverse_to:string:fg_result_view'


    security.declareProtected(View, 'isLabel')
    def isLabel(self):
        """Returns True if this field is a label and should only be
           shown in the edit form.
        """

        # override this method when field really is a label

        return False


    security.declareProtected(View, 'isFileField')
    def isFileField(self):
        """Returns True if the embedded field acts like a file field
        """

        # override if field really is file-like

        return False


    security.declareProtected(View, 'getFormPrologue')
    def getFormPrologue(self, **kw):
        """ Returns empty string to prevent display of prologue on field view """
        return ""


    security.declareProtected(View, 'getFormEpilogue')
    def getFormEpilogue(self, **kw):
        """ Returns empty string to prevent display of epilogue on field view """
        return ""


    security.declareProtected(View, 'htmlValue')
    def htmlValue(self, REQUEST):
        """ return from REQUEST, this field's value, rendered as XHTML.
        """

        # override this if a field's value from request isn't suitable for display
        # or is already in HTML

        value = REQUEST.form.get(self.__name__, 'No Input')
        valueType = type(value)

        # value may be a string or a unicode string;
        # it may be an array of string/unicode strings.
        # establish a utf-8 baseline. utf-8 not because it's right,
        # but because it will have backword compatability with previous
        # versions.
        if valueType is unicode:
            value = value.encode('utf-8')
        elif valueType is type([]):
            a = []
            for item in value:
                if type(item) is unicode:
                    item = item.encode('utf-8')
                a.append(item)
            value = a

        value = str(value)

        # eliminate square brackets around lists --
        # they mean nothing to end users
        if (valueType == type([])):
            value = value[1:-1]

        if value.find('\n') >= 0:
            # strings with embedded eols will benefit from the full
            # transform
            pt = getToolByName(self, 'portal_transforms')
            s = pt.convert('text_to_html', value).getData()
            # let's return something more semantically neutral than
            # a paragraph.
            return s.replace('<p>', '<div>').replace('</p>', '</div>')
        else:
            # don't bother with the overhead of a portal transform
            return cgi.escape(value)


    # The Archetypes file.pt macro tries -- for reasons I don't
    # really understand -- to call the field's accessor.
    # So, let's supply this as a harmless one when necessary.
    def nullAccessor(self, **kwargs):
        return None


    security.declarePublic('getFieldFormName')
    def getFieldFormName(self):
        """Returns field name as used in form and request.form.
           To be overridden when form field name varies from the field name,
           as, for example, with file field."""

        return self.fgField.getName()


    def manage_afterAdd(self, item, container):
        # TODO: when we're done with 2.1.x, implement this via event subscription

        ATCTContent.manage_afterAdd(self, item, container)

        id = self.getId()
        if self.fgField.__name__ != id:
            self.fgField.__name__ = id
