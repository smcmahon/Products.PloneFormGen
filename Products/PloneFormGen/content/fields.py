""" Form fields, implemented via Archetypes Fields, Validators and Widgets"""

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

from zope.contenttype import guess_content_type

from ZPublisher.HTTPRequest import FileUpload

from Products.Archetypes.public import *
from Products.Archetypes.utils import shasattr

from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.configuration import zconf

from Products.TALESField import TALESString, TALESLines

from Products.PloneFormGen.config import PROJECTNAME, EDIT_TALES_PERMISSION

from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo

from Products.PloneFormGen import PloneFormGenMessageFactory as _
from Products.PloneFormGen.widgets import RichLabelWidget, CaptchaWidget

from Products.PloneFormGen.content.fieldsBase import *

from types import StringTypes, BooleanType
import cgi

from DateTime import DateTime
try:
    from DateTime.interfaces import SyntaxError as DateTimeSyntaxError
    from DateTime.interfaces import DateError as DateError
except ImportError:
    DateTimeSyntaxError = DateTime.SyntaxError
    DateError = DateTime.DateError


class FGStringField(BaseFormField):
    """ A string entry field """

    security  = ClassSecurityInfo()

    schema = BaseFieldSchemaStringDefault.copy() + Schema((
        maxlengthField,
        sizeField,
        StringField('fgStringValidator',
            vocabulary='stringValidatorsDL',
            enforceVocabulary=1,
            widget=SelectionWidget(label=_(u'label_fgstringvalidator_text',
                                           default=u'Validator'),
                description=_(u'help_fgstringvalidator_text',
                  default=u"""Tests input against simple string patterns."""),
                ),
        ),
    ))

    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormStringField'
    archetype_name = 'String Field'
    content_icon = 'StringField.gif'
    typeDescription= 'A string field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = StringField('fg_string_field',
            searchable=0,
            required=0,
            write_permission = View,
            validators=('isNotTooLong',),
            )


    def stringValidatorsDL(self):
        """ return a display list of string validators.
        """

        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getStringValidatorsDL()


    def setFgStringValidator(self, value, **kw):
        """ set simple validator """

        fgt = getToolByName(self, 'formgen_tool')

        if value and (value != 'vocabulary_none_text'):
            fgtid = fgt.stringValidators[value].get('id')
            if fgtid:
                self.fgField.validators = ('isNotTooLong', fgtid)
        else:
            self.fgField.validators = ('isNotTooLong',)
        self.fgField._validationLayer()

        self.fgStringValidator = value


registerATCT(FGStringField, PROJECTNAME)


class FGPasswordField(FGStringField):
    """ Password entry field (input is masked) """

    schema = BaseFieldSchemaStringDefault.copy() + Schema((
        maxlengthField,
        sizeField,
    ))

    # attributes that are not really useful for Password field.
    del schema['hidden']
    del schema['serverSide']
    del schema['placeholder']

    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormPasswordField'
    archetype_name = 'Password Field'
    content_icon = 'PasswordField.gif'
    typeDescription= 'A password field (input masked)'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute.
        #
        # We use our own widget and reset several widget options
        # so that the password value won't be lost if form
        # validation fails.
        self.fgField = StringField('fg_string_field',
            searchable=0,
            required=0,
            write_permission = View,
            validators=('isNotTooLong',),
            widget=PasswordWidget(
                macro='pfg_password',
                populate = True,
                postback = True,
                blurrable = True,
            ),
        )

registerATCT(FGPasswordField, PROJECTNAME)


class FGIntegerField(BaseFormField):
    """ Integer entry field """

    security  = ClassSecurityInfo()

    schema = BaseFieldSchemaStringDefault.copy() + Schema((
        IntegerField('minval',
            searchable=0,
            required=1,
            default='0',
            widget=IntegerWidget(
                label=_(u'label_minval_text',
                        default=u"Minimum Acceptable Value"),
                description=_(u'help_minval_text', default=u"""
            The form will not accept values less than the number you enter here.
                """),
                ),
            ),
        IntegerField('maxval',
            searchable=0,
            required=1,
            default='10000',
            widget=IntegerWidget(
                label=_(u'label_maxval_text', default=u"Maximum Acceptable Value"),
                description=_(u'help_maxval_text', default=u"""
                    The form will not accept values greater than the number you enter here.
                """),
                ),
            ),
        maxlengthField,
        sizeField,
    ))

    # 'hidden' isn't really useful for this field.
    del schema['hidden']
    # 'serverSide' is not really useful for this field.
    del schema['serverSide']

    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormIntegerField'
    archetype_name = 'Integer Field'
    content_icon = 'IntegerField.gif'
    typeDescription= 'A integer field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = IntegerField('fg_integer_field',
            searchable=0,
            required=0,
            minval=0,
            maxval=10000,
            validators=('isNotTooLong', 'inExNumericRange',),
            write_permission = View,
            )

registerATCT(FGIntegerField, PROJECTNAME)


class FGFixedPointField(BaseFormField):
    """ Fixed-Point (float) entry field """

    security  = ClassSecurityInfo()

    schema = BaseFieldSchemaStringDefault.copy() + Schema((
        FixedPointField('minval',
            searchable=0,
            required=0,
            default='0.0',
            widget=DecimalWidget(
                label=_(u'label_minval_text',
                        default=u"Minimum Acceptable Value"),
                description=_(u'help_minval_text', default=u"""
            The form will not accept values less than the number you enter here.
                """),
                size=8,
                ),
            ),
        FixedPointField('maxval',
            searchable=0,
            required=1,
            default='10000.0',
            widget=DecimalWidget(
                label=_(u'label_maxval_text', default=u"Maximum Acceptable Value"),
                description=_(u'help_maxval_text', default=u"""
                    The form will not accept values greater than the number you enter here.
                """),
                size=8,
                ),
            ),
        maxlengthField,
        sizeField,
    ))

    # 'hidden' isn't really useful for this field.
    del schema['hidden']
    # 'serverSide' is not really useful for this field.
    del schema['serverSide']

    # and, required has only limited use ...
    schema['required'].widget.description = _(u"help_fprequired_text", default = \
        u"""NOTE: For a fixed-point field, the required flag will not allow
           entry of a '0' value.
        """)

    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormFixedPointField'
    archetype_name = 'Fixed-Point Field'
    content_icon = 'FloatField.gif'
    typeDescription= 'A fixed-point (float) field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = FixedPointField('fg_date_field',
            searchable=0,
            required=0,
            write_permission = View,
            validators=('isNotTooLong', 'inExNumericRange',),
            )

#    security.declareProtected(ModifyPortalContent, 'setThousands_commas')
#    def setThousands_commas(self, value, **kw):
#        """ set widget's thousands_commas """
#
#        self.fgField.widget.thousands_commas = value == '1'
#
#
#    security.declareProtected(ModifyPortalContent, 'getThousands_commas')
#    def getThousands_commas(self, **kw):
#        """ get widget's thousands_commas """
#
#        return self.fgField.widget.thousands_commas

registerATCT(FGFixedPointField, PROJECTNAME)


class NRBooleanField(BooleanField):
    """ A boolean field that doesn't enforce required """

    def validate_required(self, instance, value, errors):
        return None


class FGBooleanField(BaseFormField):
    """ Boolean (checkbox) field """

    security  = ClassSecurityInfo()

    schema = BaseFieldSchema.copy() + Schema((
        StringField('fgDefault',
            searchable=0,
            required=0,
            widget=BooleanWidget(
                label=_(u'label_fgdefault_text', default=u'Default'),
                description=_(u'help_fgdefault_text', default=u"The value the "
                    "field should contain when the form is first displayed."
                    "Note that this may be overridden dynamically."),
                ),
        ),
        StringField('fgBooleanValidator',
            vocabulary='boolVocabDL',
            enforceVocabulary=1,
            widget=SelectionWidget(label=_(u'label_fgbooleanvalidator_text', default=u'Validator'),
                description=_(u'help_fgbooleanvalidator_text', default=u"""Choose a validator to require a particular response."""),
                ),
        ),
        StringField('fgBoolTrueString',
            required=0,
            searchable=0,
            default='1',
            widget=StringWidget(
                label=_(u'label_fgbooleantruestring_text', default=u"True Display String"),
                description=_(u'help_fgbooleantruestring_text', default=\
                    u"String to use in thanks page and mail when the field's "
                    "checkbox is checked."),
                ),
            ),
        StringField('fgBoolFalseString',
            required=0,
            searchable=0,
            default='0',
            widget=StringWidget(
                label=_(u'label_fgbooleanfalsestring_text', default=u"False Display String"),
                description=_(u'help_fgbooleanfalsestring_text', default=u"""String to use in thanks page and mail when the field's checkbox is unchecked."""),
                ),
            ),
    ))
    schema['required'].widget.description = \
        _(u'help_boolrequired_text', default=u"""NOTE: For a checkbox field, the required flag doesn't do anything beyond
           putting a 'required' marker next to the label. If you wish to require a
           particular input, choose a validator below.
        """)

    # attributes that are not really useful for Boolean field.
    del schema['hidden']
    del schema['serverSide']
    del schema['placeholder']

    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormBooleanField'
    archetype_name = 'Boolean Field'
    content_icon = 'CheckBoxField.gif'
    typeDescription= 'A CheckBox (Boolean) field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = NRBooleanField('fg_boolean_field',
            searchable=0,
            required=0,
            write_permission = View,
            )

    security.declareProtected(ModifyPortalContent, 'setFgBooleanValidator')
    def setFgBooleanValidator(self, value, **kw):
        """ set boolean validator """

        if value:
            self.fgField.validators = (value,)
        else:
            self.fgField.validators = ()
        self.fgField._validationLayer()

        self.fgBooleanValidator = value


    def boolVocabDL(self):
        """ returns DisplayList of vocabulary for fgBooleanValidator """

        return DisplayList( (
            ('',
                _(u'vocabulary_none_text', u'None')
                ),
            ('isChecked',
                _(u'vocabulary_ischecked_text', u'Is checked')
                ),
            ('isUnchecked',
                _(u'vocabulary_isnotchecked_text', u'Is not checked')
                ),
            ) )


    def htmlValue(self, REQUEST):
        """ Return value instead of key """

        value = REQUEST.form.get(self.__name__, 'No Input')
        if type(value) == BooleanType:
            if value:
                return self.fgBoolTrueString
        elif value == '1':
            return self.fgBoolTrueString

        return self.fgBoolFalseString



registerATCT(FGBooleanField, PROJECTNAME)


class FGDateField(BaseFormField):
    """ Date/Time Entry Field """

    security  = ClassSecurityInfo()

    schema = BaseFieldSchemaStringDefault.copy() + Schema((
        BooleanField('fgShowHM',
            searchable=0,
            required=0,
            default=1,
            widget=BooleanWidget(
                label=_(u'label_fgshowhm_text', default=u'Show Time Selection Options'),
                description=_(u'help_fgshowhm_text', default=u''),
                ),
        ),
        IntegerField('fgStartingYear',
            searchable=0,
            required=0,
            default='1999',
            widget=IntegerWidget(
                label=_(u'label_fgstartingyear_text', default=u'Starting Year'),
                description = _(u"help_fgstartingyear_text"),
                ),
        ),
        IntegerField('fgEndingYear',
            searchable=0,
            required=0,
            default=None,
            widget=IntegerWidget(
                label=_(u'label_fgendingyear_text', default=u'Ending Year'),
                description = _(u'help_fgendingyear_text', default=u"""The last year to offer in the year drop-down.
                 Leave this empty if you wish to instead use a number of future years."""),
                ),
        ),
        IntegerField('fgFutureYears',
            searchable=0,
            required=0,
            default='5',
            widget=IntegerWidget(
                label=_(u'label_fgfutureyears_text', default=u'Future Years To Display'),
                description = _(u'help_fgfutureyears_text', default=u"""The number of future years to offer in the year drop-down.
                 (This is only applicable if you have not specified an ending year.)"""),
                ),
        ),
))

    # attributes that are not really useful for Date/Time field.
    del schema['hidden']
    del schema['serverSide']
    del schema['placeholder']

    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormDateField'
    archetype_name = 'Date/Time Field'
    content_icon = 'DateTimeField.gif'
    typeDescription= 'A date/time field. Time component is optional.'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = DateTimeField('fg_date_field',
            searchable=0,
            required=0,
            write_permission = View,
            widget=CalendarWidget(),
            )


    security.declareProtected(ModifyPortalContent, 'setFgShowHM')
    def setFgShowHM(self, value, **kw):
        """ set show_hm """

        if type(value) == BooleanType:
            self.fgField.widget.show_hm = value
        else:
            self.fgField.widget.show_hm = value == '1'

        self.fgShowHM = value


    security.declareProtected(ModifyPortalContent, 'setFgStartingYear')
    def setFgStartingYear(self, value, **kw):
        """ set starting_year """

        if value:
            try:
                self.fgField.widget.starting_year = int(value)
                self.fgStartingYear = value
            except ValueError:
                pass
        else:
            self.fgField.widget.starting_year = None
            self.fgStartingYear = value


    security.declareProtected(ModifyPortalContent, 'setFgEndingYear')
    def setFgEndingYear(self, value, **kw):
        """ set ending_year """

        if value:
            try:
                self.fgField.widget.ending_year = int(value)
                self.fgEndingYear = value
            except ValueError:
                pass
        else:
            self.fgField.widget.ending_year = None
            self.fgEndingYear = value


    security.declareProtected(ModifyPortalContent, 'setFgFutureYears')
    def setFgFutureYears(self, value, **kw):
        """ set future_years """

        if value:
            try:
                self.fgField.widget.future_years = int(value)
                self.fgFutureYears = value
            except ValueError:
                pass
        else:
            self.fgField.widget.future_years = None
            self.fgFutureYears = value


    def _toLocalizedTime(self, time, long_format=None):
        tool = getToolByName(self, 'translation_service')
        return tool.ulocalized_time(time, long_format=long_format)


    def htmlValue(self, REQUEST):
        """ return from REQUEST, this field's value, rendered as XHTML.
        """

        value = REQUEST.form.get(self.__name__, 'No Input')

        # The replace('-','/') keeps the DateTime routine from
        # interpreting this as UTC. Odd, but true.

        try:
            dt = DateTime(value.replace('-','/'))
        except (DateTimeSyntaxError, DateError):
            # probably better to simply return the input
            return cgi.escape(value)

        if self.fgField.widget.show_hm:
            value = self._toLocalizedTime(dt, long_format=True)
        else:
            value = self._toLocalizedTime(dt)

        return cgi.escape(value)


    def specialValidator(self, value, field, REQUEST, errors):
        """ Archetypes isn't validating non-required dates --
            so we need to.
        """

        fname = field.getName()
        month = REQUEST.form.get('%s_month'%fname, '01')
        day = REQUEST.form.get('%s_month'%fname, '01')

        if (month == '00') and (day == '00'):
            value = ''
            REQUEST.form[fname] = ''

        if value and not field.required:
            try:
                dt = DateTime(value)
            except (DateTimeSyntaxError, DateError):
                return "Validation failed(isValidDate): this is not a valid date."
        return 0


registerATCT(FGDateField, PROJECTNAME)


class FGLabelField(BaseFormField):
    """ Label-Only field (no input component) """

    security  = ClassSecurityInfo()

    schema = BareFieldSchema.copy()
    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormLabelField'
    archetype_name = 'Label Field'
    content_icon = 'LabelField.gif'
    typeDescription= 'A Label (No Input) field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = StringField('fg_label_field',
            searchable=0,
            required=0,
            write_permission = View,
            widget=LabelWidget(),
            )

    def isLabel(self):
        return True

registerATCT(FGLabelField, PROJECTNAME)


class FGLinesField(BaseFormField):
    """ A line entry field. This appears as a textarea without wordwrap. """

    security  = ClassSecurityInfo()

    schema = BaseFieldSchemaLinesDefault.copy()

    # Standard content type setup
    portal_type = meta_type = 'FormLinesField'
    archetype_name = 'Lines Field'
    content_icon = 'LinesField.gif'
    typeDescription= 'A lines field. This appears as a textarea without wordwrap.'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = LinesField('fg_lines_field',
            searchable=0,
            required=0,
            write_permission = View,
            )

    def fgPrimeDefaults(self, request, contextObject=None):
        """ primes request with default """

        # the lines widget will choke if there is no value
        BaseFormField.fgPrimeDefaults(self, request, contextObject)
        request.form.setdefault(self.fgField.__name__, ['',])


registerATCT(FGLinesField, PROJECTNAME)


class FGSelectionField(BaseFormField):
    """ Selection Field (radio buttons or select) """

    security  = ClassSecurityInfo()

    schema = BaseFieldSchemaStringDefault.copy() + Schema((
        vocabularyField,
        vocabularyOverrideField,
        StringField('fgFormat',
            searchable=0,
            required=0,
            default='flex',
            enforceVocabulary=1,
            vocabulary='formatVocabDL',
            widget=SelectionWidget(
                label=_(u'label_fgformat_text', default=u'Presentation Widget'),
                description=_(u'help_fgformat_text', default=u''),
                ),
        ),
    ))

    # attributes that are not really useful for a selection field.
    # Just use a hidden string field if you really need this.
    del schema['hidden']
    del schema['serverSide']
    del schema['placeholder']

    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormSelectionField'
    archetype_name = 'Selection Field'
    content_icon = 'ListField.gif'
    typeDescription= 'A selection field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = StringVocabularyField('fg_selection_field',
            searchable=0,
            required=0,
            widget=SelectionWidget(),
            vocabulary = '_get_selection_vocab',
            enforceVocabulary=1,
            write_permission = View,
            )


    security.declareProtected(ModifyPortalContent, 'setFgFormat')
    def setFgFormat(self, value, **kw):
        """ set selection format """

        self.fgField.widget.format = value
        self.fgFormat = value


    def formatVocabDL(self):
        """ returns vocabulary for fgFormat """

        return DisplayList( (
            ('flex',
                    _(u'vocabulary_flex_text', u'Flexible (radio for short, select for longer)')
                ),
            ('select',
                    _(u'vocabulary_selection_text', u'Selection list')
                ),
            ('radio',
                    _(u'vocabulary_radio_text', u'Radio buttons')
                ),
        ) )


    def htmlValue(self, REQUEST):
        """ Return value instead of key """

        utils = getToolByName(self, 'plone_utils')
        charset = utils.getSiteEncoding()

        value = REQUEST.form.get(self.__name__, '')

        # note that vocabulary items are in unicode;
        # so, we must decode before lookup
        vu = value.decode(charset)

        vocabulary = self.fgField.Vocabulary(self)
        v = vocabulary.getValue(vu) or vu

        # v might be unicode or string.  We need string.
        if isinstance(v, unicode):
            v = v.encode(charset)
        return cgi.escape(v)


registerATCT(FGSelectionField, PROJECTNAME)


class FGMultiSelectField(BaseFormField):
    """ Multiple selection field (select with multiple or check boxes) """

    security  = ClassSecurityInfo()

    schema = BaseFieldSchemaLinesDefault.copy() + Schema((
        vocabularyField,
        vocabularyOverrideField,
        StringField('fgFormat',
            searchable=0,
            required=0,
            default='select',
            enforceVocabulary=1,
            vocabulary='formatVocabDL',
            widget=SelectionWidget(
                label=_(u'label_fgmsformat_text', default=u'Presentation Widget'),
                description=_(u'help_fgmsformat_text', default=u"""Useful for stopping spam"""),
                ),
        ),
    ))

    # current Archetypes doesn't really support hidden for
    # multi-select. Use a lines field if you really need this
    del schema['hidden']
    del schema['serverSide']
    del schema['placeholder']

    # hide references & discussion
    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormMultiSelectionField'
    archetype_name = 'Multi-Select Field'
    content_icon = 'MultipleListField.gif'
    typeDescription= 'A multiple-selection field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = LinesVocabularyField('fg_mselection_field',
            searchable=0,
            required=0,
            widget=MultiSelectionWidget(),
            vocabulary = '_get_selection_vocab',
            enforceVocabulary=1,
            write_permission = View,
            )


    security.declareProtected(ModifyPortalContent, 'setFgFormat')
    def setFgFormat(self, value, **kw):
        """ set selection format """

        self.fgField.widget.format = value
        self.fgFormat = value


    security.declareProtected(ModifyPortalContent, 'setFgRows')
    def setFgRows(self, value, **kw):
        """ sets widget rows """

        self.fgField.widget.size = value


    security.declareProtected(View, 'getFgRows')
    def getFgRows(self, **kw):
        """ gets widget rows """

        return self.fgField.widget.size


    def formatVocabDL(self):
        """ returns vocabulary for fgFormat """

        return DisplayList( (
            ('select',
                    _(u'vocabulary_selection_text', u'Selection list')
                ),
            ('checkbox',
                    _(u'vocabulary_checkbox_text', u'Checkbox list')
                )
            ) )


    def htmlValue(self, REQUEST):
        """ Return value instead of key """

        utils = getToolByName(self, 'plone_utils')
        charset = utils.getSiteEncoding()

        value = REQUEST.form.get(self.__name__, [])

        vocabulary = self.fgField.Vocabulary(self)
        result = []
        for k in value:
            # there'll be an empty string to avoid
            if len(k):
                # vocabulary items are in unicode;
                # so decode the key before lookup
                ku = k.decode(charset)
                v = vocabulary.getValue(ku) or ku
                # v might be unicode or string.  We need string.
                if isinstance(v, unicode):
                    v = v.encode(charset)
                result.append(v)

        value = ', '.join(result)

        return cgi.escape(value)


registerATCT(FGMultiSelectField, PROJECTNAME)


class PlainTextField(TextField):
    """
    A text field forced text/plain.
    Without this hack, the textarea widget will (by acquisition) call
    the form folder's getContentType method.

    Also, the getAllowedContentTypes method override solves a problem
    in Plone 3 where old instances of a text field with None set for
    allowed_content_types were badly handled by the new getAllowedContentTypes
    method in TextField -- which used site mimetype defaults.
    """

    security  = ClassSecurityInfo()

    security.declarePublic('getContentType')
    def getContentType(self, instance, fromBaseUnit=True):
        return 'text/plain'

    security.declarePublic('getAllowedContentTypes')
    def getAllowedContentTypes(self, instance):
        return 'text/plain'


class FGTextField(BaseFormField):
    """ Text (textarea) field """

    security  = ClassSecurityInfo()

    schema = BaseFieldSchemaTextDefault.copy()
    schema += Schema((
        BooleanField('validateNoLinkSpam',
            searchable=0,
            required=0,
            default=False,
            widget=BooleanWidget(
                label=_(u'label_validate_link_spam_text', default=u"Reject Text with Links?"),
                description=_(u'help_validate_link_spam_text', default=u"""Useful for stopping spam"""),
                ),
            ),
        ))

    # Standard content type setup
    portal_type = meta_type = 'FormTextField'
    archetype_name = 'Text Field'
    content_icon = 'TextAreaField.gif'
    typeDescription= 'A text area field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = PlainTextField('fg_text_field',
            searchable=0,
            required=0,
            write_permission = View,
            validators=('isNotTooLong','isNotLinkSpam',),
            default_content_type = 'text/plain',
            allowable_content_types = ('text/plain',),
            widget = TextAreaWidget(
                maxlength=0,
                ),
            validate_no_link_spam = 0,
            )

    security.declareProtected(View, 'isBinary')
    def isBinary(self, key):
        return False

    security.declareProtected(View, 'getContentType')
    def getContentType(self, key=None):
        return 'text/plain'

    def setValidateNoLinkSpam(self, value):
        """
        for BBB, to make sure the validator gets enabled on legacy text fields
        """
        self.fgField.validators = ('isNotTooLong', 'isNotLinkSpam')
        self.fgField._validationLayer()

        self.fgField.validate_no_link_spam = value

    def getValidateNoLinkSpam(self):
        return getattr(self.fgField, 'validate_no_link_spam', 0)

registerATCT(FGTextField, PROJECTNAME)


class HtmlTextField(TextField):
    """
    A text field forced text/html.
    Without this hack, the rich widget will (by acquisition) call
    the form folder's getContentType method.
    """

    security  = ClassSecurityInfo()

    security.declarePublic('getContentType')
    def getContentType(self, instance, fromBaseUnit=True):
        return 'text/html'


class FGRichTextField(BaseFormField):
    """ Rich-text (visual editor) field """

    from Products.ATContentTypes.config import HAS_MX_TIDY

    security  = ClassSecurityInfo()

    schema = BaseFieldSchemaRichTextDefault.copy()

    # attributes that are not really useful for an RT field.
    # Just use a hidden string field if you really need this.
    del schema['hidden']
    del schema['serverSide']
    del schema['placeholder']

    if HAS_MX_TIDY:
        schema = schema + Schema((
            StringField('fgStringValidator',
                vocabulary='htmlValidatorsDL',
                enforceVocabulary=1,
                default='isTidyHtmlWithCleanup',
                widget=SelectionWidget(label=_(u'label_fgstringvalidator_text', default=u'Validator'),
                    description=_(u'help_fgrtvalidator_text', default=u"""Input tests using HTMLTidy (if installed)."""),
                    ),
                ),
        ))

    # Standard content type setup
    portal_type = meta_type = 'FormRichTextField'
    archetype_name = 'RichText Field'
    content_icon = 'RichTextField.gif'
    typeDescription= 'A rich text area field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = HtmlTextField('fg_text_field',
            searchable=0,
            required=0,
            write_permission = View,
            validators = ('isNotTooLong', 'isTidyHtmlWithCleanup',),
            default_content_type = 'text/html',
            default_output_type = 'text/x-html-safe',
            allowable_content_types = zconf.ATDocument.allowed_content_types,
            widget = RichWidget(
                    allow_file_upload = False,
                    ),
            )


    security.declareProtected(View, 'isBinary')
    def isBinary(self, key):
        return False;

    security.declareProtected(View, 'getContentType')
    def getContentType(self, key=None):
        return 'text/html'

    def htmlValidatorsDL(self):
        """ return a display list of string validators.
            this is a hack for 118n
        """

        return DisplayList( (
            ('',
                _(u'vocabulary_none_text', u'None')
                ),
            ('isTidyHtml',
                _(u'vocabulary_istidyhtml_text', u'Is Tidy HTML (fails on errors and warnings)')
                ),
            ('isTidyHtmlWithCleanup',
                _(u'vocabulary_istidyhtmlwithcleanup_text', u'Tidy HTML With Cleanup (fails on errors, cleans up rest)')
                ),
            ) )

    def htmlValue(self, REQUEST):
        """ override, as this field is already html.
        """

        return REQUEST.form.get(self.__name__, 'No Input')


registerATCT(FGRichTextField, PROJECTNAME)


class FGRichLabelField(BaseFormField):
    """ Rich-text label field """

    security  = ClassSecurityInfo()

    schema = BareFieldSchema.copy() + Schema((
        HtmlTextField('fgDefault',
            searchable=0,
            required=0,
            validators = ('isTidyHtmlWithCleanup',),
            default_content_type = 'text/html',
            default_output_type = 'text/x-html-safe',
            allowable_content_types = zconf.ATDocument.allowed_content_types,
            widget=RichWidget(label=_(u'label_fglabelbody_text', default=u'Label body'),
                description=_(u'help_fglabelbody_text', default=u"""
                    The text to display in the form.
                """),
                allow_file_upload = False,
                ),
            ),
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
        ))

    schema['title'].widget.label = _(u'label_title', default=u"Title")
    schema['title'].widget.description = _(u'help_notdisplayed_text', default=u"Not displayed on form.")
    schema['description'].widget.visible = {'view':'invisible','edit':'invisible'}

    # Standard content type setup
    portal_type = meta_type = 'FormRichLabelField'
    archetype_name = 'Rich Label Field'
    content_icon = 'RichLabelField.gif'
    typeDescription= 'A rich-text label'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = HtmlTextField('fg_text_field',
            searchable=0,
            required=0,
            write_permission = View,
            default_content_type = 'text/html',
            default_output_type = 'text/x-html-safe',
            allowable_content_types = zconf.ATDocument.allowed_content_types,
            widget = RichLabelWidget(),
            )

    security.declareProtected(ModifyPortalContent, 'setFgDefault')
    def setFgDefault(self, value, **kw):
        """ set default for field """

        self.fgField.default = value

    def getRawFgDefault(self, **kw):
        """ get default for field """

        return self.fgField.default

    security.declareProtected(View, 'isBinary')
    def isBinary(self, key):
        return False;

    security.declareProtected(View, 'getContentType')
    def getContentType(self, key=None):
        return 'text/html'

    def isLabel(self):
        return True

registerATCT(FGRichLabelField, PROJECTNAME)


class FGFileField(BaseFormField):
    """ File (upload) field """

    security  = ClassSecurityInfo()

    schema = BaseFieldSchema.copy() + Schema((
        StringField('fgMaxMB',
            searchable=0,
            required=0,
            default=0,
            widget=IntegerWidget(
                label=_(u'label_filemaxmb_text', default=u'Maximum Upload Size (Megabytes)'),
                description=_(u'help_filemaxmb_text', default=u"""Set to 0 for no limit."""),
                ),
        ),

    ))

    # attributes that are not really useful for a file field.
    del schema['hidden']
    del schema['serverSide']
    del schema['placeholder']

    finalizeFieldSchema(schema, folderish=True, moveDiscussion=False)

    # Standard content type setup
    portal_type = meta_type = 'FormFileField'
    archetype_name = 'File Field'
    content_icon = 'FileField.gif'
    typeDescription= 'A file field'

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = FileField('fg_file_field',
            searchable=0,
            required=0,
            write_permission = View,
            accessor = 'nullAccessor',
            maxsize=0,
            validators=('isMaxSize',),
            )

    def isFileField(self):
        return True

    security.declareProtected(ModifyPortalContent, 'setFgMaxMB')
    def setFgMaxMB(self, value, **kw):
        """ set the maxmb """

        self.fgField.maxsize = int(value)

    security.declareProtected(View, 'getFgMaxMB')
    def getFgMaxMB(self, **kw):
        """ get the maxmb """

        return self.fgField.maxsize

    def htmlValue(self, REQUEST):

        file = REQUEST.form.get('%s_file' % self.fgField.getName())
        if isinstance(file, FileUpload) and file.filename != '':
            file.seek(0)
            fdata = file.read()
            filename = file.filename
            mimetype, enc = guess_content_type(filename, fdata, None)
            return "%s: %s bytes" % (mimetype, len(fdata))
        else:
            return 'No Input'

    def getFieldFormName(self):
        """field widget appends '_file' file to field id"""

        return self.fgField.getName() + '_file'

    # some File methods to make the FGFileField behave like a file object
    # this solves an issue with Archetype trying to read the file and
    # determine the mime type

    def seek(self, offset, whence=None):
        return

    def read(self, size=None):
        return ''

    def tell(self):
        return 0

registerATCT(FGFileField, PROJECTNAME)


class FGCaptchaField(FGStringField):

    meta_type = 'FormCaptchaField'
    content_icon = 'CaptchaField.gif'

    schema = BaseFieldSchemaStringDefault.copy()

    # some attributes that don't make sense for a CAPTCHA field
    del schema['required']
    del schema['hidden']
    del schema['placeholder']
    noview = {'view': 'invisible', 'edit': 'invisible'}
    schema['fgDefault'].widget.visible = noview
    schema['fgTDefault'].widget.visible = noview
    schema['fgTValidator'].widget.visible = noview
    schema['serverSide'].widget.visible = noview


    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseFormField.__init__(self, oid, **kwargs)

        # set a preconfigured field as an instance attribute
        self.fgField = StringField('fg_string_field',
            searchable = 0,
            required = 1,
            write_permission = View,
            validators = ('isCorrectCaptcha',),
            widget = CaptchaWidget(),
            )

registerATCT(FGCaptchaField, PROJECTNAME)


from Products.PloneFormGen.widgets import \
    FieldsetStartWidget, FieldsetEndWidget

class FGFieldsetStart(BaseFormField):
    """ Marks start of fieldset (no input component) """

    security  = ClassSecurityInfo()

    schema =  BaseFieldSchema.copy()
    del schema['hidden']
    del schema['placeholder']
    noview = {'view': 'invisible', 'edit': 'invisible'}
    schema['fgTEnabled'].widget.visible = noview
    schema['fgTDefault'].widget.visible = noview
    schema['fgTValidator'].widget.visible = noview
    schema['serverSide'].widget.visible = noview

    schema['required'].default = True
    schema['required'].widget.label = _(u'label_showlegend_text', default=u'Show Title as Legend')
    schema['required'].widget.description=_(u'help_showlegend_text', default=u'')

    # Standard content type setup
    portal_type = meta_type = 'FieldsetStart'
    archetype_name = 'Fieldset Beginning'
    content_icon = 'LabelField.gif'
    typeDescription= 'Start a fieldset'

    _at_rename_after_creation = True

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseObject.__init__(self, oid, **kwargs)

        self.fgField = StringField('fg_fieldset_start',
            searchable=0,
            required=0,
            default='1',
            write_permission = View,
            widget=FieldsetStartWidget(),
            )

    security.declareProtected(View, 'isLabel')
    def isLabel(self):
        """ yes, this is just decorative """
        return True

    security.declareProtected(ModifyPortalContent, 'setRequired')
    def setRequired(self, value, **kw):
        """ double purpose required field as show_legend field
            so that we may update easily with the quick editor
        """
        if type(value) == BooleanType:
            self.fgField.widget.show_legend = value
            self.fgField.required = value
        else:
            self.fgField.widget.show_legend = value == '1' or value == 'True'
            self.fgField.required = value == '1' or value == 'True'

registerType(FGFieldsetStart, PROJECTNAME)


class FGFieldsetEnd(BaseFormField):
    """ Marks end of fieldset (no input component) """

    security  = ClassSecurityInfo()

    schema =  BaseFieldSchema.copy()

    # Standard content type setup
    portal_type = meta_type = 'FieldsetEnd'
    archetype_name = 'Fieldset End'
    content_icon = 'LabelField.gif'
    typeDescription= 'End a fieldset'

    _at_rename_after_creation = False

    del schema['hidden']
    del schema['placeholder']
    noview = {'view': 'invisible', 'edit': 'invisible'}
    schema['fgTEnabled'].widget.visible = noview
    schema['fgTDefault'].widget.visible = noview
    schema['fgTValidator'].widget.visible = noview
    schema['serverSide'].widget.visible = noview
    schema['required'].widget.visible = noview
    schema['description'].widget.visible = noview
    schema['title'].widget.visible = noview

    def __init__(self, oid, **kwargs):
        """ initialize class """

        BaseObject.__init__(self, oid, **kwargs)

        self.fgField = StringField('FieldsetEnd',
            searchable=0,
            required=0,
            write_permission = View,
            widget=FieldsetEndWidget(),
            )

    security.declareProtected(ModifyPortalContent, 'setId')
    def setId(self, value):
        """Sets the object id. Changes both object and field id.
        """

        BaseContent.setId(self, value)
        self.fgField.__name__ = self.getId()
        self.setTitle(value)

    security.declareProtected(View, 'isLabel')
    def isLabel(self):
        """ yes, this is just decorative """
        return True

registerType(FGFieldsetEnd, PROJECTNAME)
