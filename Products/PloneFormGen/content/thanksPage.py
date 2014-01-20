"""thanksPage -- A smart(er) thank-you page for PloneFormGen"""

__author__ = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

from zope.interface import implements

from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.Archetypes.public import *
from Products.Archetypes.utils import shasattr
from Products.Archetypes.interfaces.field import IField

from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.configuration import zconf

from Products.PloneFormGen.config import PROJECTNAME
from Products.PloneFormGen.interfaces import IPloneFormGenThanksPage

from Products.PloneFormGen import PloneFormGenMessageFactory as _
from Products.PloneFormGen import dollarReplace

import zope.i18n


ThanksPageSchema = ATContentTypeSchema.copy() + Schema((
    BooleanField('showAll',
        required=0,
        searchable=0,
        default='1',
        widget=BooleanWidget(
            label=_(u'label_showallfields_text', default=u"Show All Fields"),
            description=_(u'help_showallfields_text', default=u"""
                Check this to display input for all fields
                (except label and file fields). If you check
                this, the choices in the pick box below
                will be ignored.
                """),
            ),
        ),
    LinesField('showFields',
        required=0,
        searchable=0,
        vocabulary='fieldDisplayList',
        widget=PicklistWidget(
            label=_(u'label_showfields_text', default=u"Show Responses"),
            description=_(u'help_showfields_text', default=u"""
                Pick the fields whose inputs you'd like to display on
                the success page.
                """),
            ),
        ),
    BooleanField('includeEmpties',
        required=0,
        searchable=0,
        default='1',
        widget=BooleanWidget(
            label=_(u'label_includeEmpties_text', default=u"Include Empties"),
            description=_(u'help_includeEmpties_text', default=u"""
                Check this to display field titles
                for fields that received no input. Uncheck
                to leave fields with no input off the list.
                """),
            ),
        ),
    TextField('thanksPrologue',
        schemata='decoration',
        required=False,
        searchable=False,
        primary=False,
        accessor='getThanksPrologue',
        validators=('isTidyHtmlWithCleanup',),
        default_content_type=zconf.ATDocument.default_content_type,
        default_output_type='text/x-html-safe',
        allowable_content_types=zconf.ATDocument.allowed_content_types,
        widget=RichWidget(
            label=_(u"label_thanksprologue_text", default=u"Thanks Prologue"),
            description=_(u"help_thanksprologue_text", default=u"This text will be displayed above the selected field inputs."),
            rows=8,
            allow_file_upload=zconf.ATDocument.allow_document_upload,
            ),
        ),
    TextField('thanksEpilogue',
        schemata='decoration',
        required=False,
        searchable=False,
        primary=False,
        accessor='getThanksEpilogue',
        validators=('isTidyHtmlWithCleanup',),
        default_content_type=zconf.ATDocument.default_content_type,
        default_output_type='text/x-html-safe',
        allowable_content_types=zconf.ATDocument.allowed_content_types,
        widget=RichWidget(
            label=_(u"label_thanksepilogue_text", default=u"Thanks Epilogue"),
            description=_(u"help_thanksepilogue_text", default=u"The text will be displayed after the field inputs."),
            rows=8,
            allow_file_upload=zconf.ATDocument.allow_document_upload,
            ),
        ),
    TextField('noSubmitMessage',
        schemata='no-input',
        required=False,
        searchable=False,
        primary=False,
        validators=('isTidyHtmlWithCleanup',),
        default_content_type=zconf.ATDocument.default_content_type,
        default_output_type='text/x-html-safe',
        default="""
            <p>No input was received. Please <a title="Test Folder" href=".">visit the form</a>.</p>
            """,
        allowable_content_types=zconf.ATDocument.allowed_content_types,
        widget=RichWidget(
            label=_(u"label_nosubmit_text", default=u"No Submit Message"),
            description=_(u"help_nosubmit_text", default=u"""
                The text to display if the browser reaches this
                thanks page without submitting a form. Typically, this
                would direct the reader to the form.
                """),
            rows=4,
            allow_file_upload=zconf.ATDocument.allow_document_upload,
            ),
        ),
    ))


finalizeATCTSchema(ThanksPageSchema, folderish=True, moveDiscussion=False)
# As of P3.0, rich text fields on non-default schema
# still don't function.
# Reorganize schema as well as possible.
ThanksPageSchema['thanksPrologue'].schemata = 'default'
ThanksPageSchema['thanksEpilogue'].schemata = 'default'
ThanksPageSchema['noSubmitMessage'].schemata = 'default'
ThanksPageSchema['includeEmpties'].schemata = 'fields'
ThanksPageSchema['showAll'].schemata = 'fields'
ThanksPageSchema['showFields'].schemata = 'fields'
# simplify schema
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
               'excludeFromNav', ):
    ThanksPageSchema[afield].widget.visible = {'view': 'invisible', 'edit': 'invisible'}
    ThanksPageSchema[afield].schemata = 'default'

NO_TRAVERSE = (
    'thanksPrologue',
    'thanksEpilogue',
    'noSubmitMessage',
    )


class FormThanksPage(ATCTContent):
    """A thank-you page that can display form input"""

    implements(IPloneFormGenThanksPage)

    schema = ThanksPageSchema

    content_icon   = 'ThanksPage.gif'
    meta_type      = 'FormThanksPage'
    portal_type    = 'FormThanksPage'
    archetype_name = 'Thanks Page'

    immediate_view = 'fg_thankspage_view'
    default_view   = 'fg_thankspage_view'
    suppl_views = ()

    typeDescription = 'A thank-you page that can display form input.'

    global_allow = 0

    security       = ClassSecurityInfo()

    def __bobo_traverse__(self, REQUEST, name):
        # prevent traversal to attributes we want to protect
        if name in NO_TRAVERSE:
            raise AttributeError
        return super(FormThanksPage, self).__bobo_traverse__(REQUEST, name)

    def initializeArchetype(self, **kwargs):
        """ Translate the adapter in the current langage
        """

        ATCTContent.initializeArchetype(self, **kwargs)

        self.setNoSubmitMessage(zope.i18n.translate(_(u'pfg_thankspage_nosubmitmessage', u'<p>No input was received. Please visit the form.</p>'), context=self.REQUEST))

    security.declareProtected(View, 'fieldDisplayList')
    def fieldDisplayList(self):
        """ returns a DisplayList of all fields """

        return self.fgFieldsDisplayList()

    security.declareProtected(View, 'displayFields')
    def displayFields(self):
        """ Returns a list of fields that should be
            displayed on the thanks page.
        """
        if self.showAll:
            # acquire field list from parent
            return self.fgFields(displayOnly=True)

        # acquire field list from parent
        fields = self.fgFields()
        res = []
        for id in self.showFields:
            # inefficient if we get many fields
            for f in fields:
                if f.getName() == id:
                    res.append(f)
                    break
        return res

    security.declareProtected(View, 'displayInputs')
    def displayInputs(self, request):
        """ Returns sequence of dicts {'label':fieldlabel, 'value':input}
        """
        # get a list of all candidate fields
        myFields = []
        for obj in self.aq_parent._getFieldObjects():
            if not (IField.providedBy(obj) or obj.isLabel()):
                # if field list hasn't been specified explicitly, exclude server side fields
                if self.showAll and obj.getServerSide():
                    continue
                myFields.append(obj)

        # Now, determine which fields we show
        if self.showAll:
            sFields = myFields
        else:
            sFields = []
            # acquire field list from parent
            res = []
            for id in self.showFields:
                # inefficient if we get many fields
                for f in myFields:
                    if f.getId() == id:
                        sFields.append(f)
                        break

        # Now, build the results list
        res = []
        for obj in sFields:
            value = obj.htmlValue(request)
            if self.includeEmpties or (value and (value != 'No Input')):
                res.append({
                    'label': obj.fgField.widget.label,
                    'value': value,
                    })

        return res


    security.declareProtected(ModifyPortalContent, 'setShowFields')
    def setShowFields(self, value, **kw):
        """ Reorder form input to match field order """
        # This wouldn't be desirable if the PickWidget
        # retained order.

        self.showFields = []
        for field in self.fgFields(excludeServerSide=False):
            id = field.getName()
            if id in value:
                self.showFields.append(id)


    security.declarePrivate('_dreplace')
    def _dreplace(self, s):
        request = getattr(self, 'REQUEST', {})
        return dollarReplace.DollarVarReplacer(getattr(request, 'form', {})).sub(s)


    security.declarePublic('getThanksPrologue')
    def getThanksPrologue(self):
        """ get expanded prologue """

        return self._dreplace(self.getRawThanksPrologue())


    security.declarePublic('getThanksEpilogue')
    def getThanksEpilogue(self):
        """ get expanded epilogue """

        return self._dreplace(self.getRawThanksEpilogue())


registerATCT(FormThanksPage, PROJECTNAME)
