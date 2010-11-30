"""
 A form action adapter that e-mails input.
"""

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'


########################
# The formMailerAdapter code and schema borrow heavily
# from PloneFormMailer <http://plone.org/products/ploneformmailer>
# by Jens Klein and Reinout van Rees.
#
# Author:       Jens Klein <jens.klein@jensquadrat.com>
#
# Copyright:    (c) 2004 by jens quadrat, Klein & Partner KEG, Austria
# Licence:      GNU General Public Licence (GPL) Version 2 or later
#######################

from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.Archetypes.utils import OrderedDict
from Products.Archetypes.utils import shasattr

from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT

from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName

from Products.PloneFormGen.config import *
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, FormAdapterSchema

from Products.TALESField import TALESString
from Products.TemplateFields import ZPTField as ZPTField

from ya_gpg import gpg

from email import Encoders
from email.Header import Header
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from types import StringTypes

from Products.PloneFormGen import PloneFormGenMessageFactory as _
from Products.PloneFormGen import dollarReplace

try:
    # 3.0+
    from zope.contenttype import guess_content_type
except ImportError:
    # 2.5.x
    from zope.app.content_types import guess_content_type

import zope.i18n


formMailerAdapterSchema = FormAdapterSchema.copy() + Schema((
    StringField('recipient_name',
        searchable=0,
        required=0,
        default_method='getDefaultRecipientName',
        write_permission=EDIT_ADDRESSING_PERMISSION,
        read_permission=ModifyPortalContent,
        widget=StringWidget(
            label = _(u'label_formmailer_recipient_fullname',
                      default=u"Recipient's full name"),
            description = _(u'help_formmailer_recipient_fullname', default=u"""
                The full name of the recipient of the mailed form.
                """),
            ),
        ),
    StringField('recipient_email',
        searchable=0,
        required=0,
        default_method='getDefaultRecipient',
        write_permission=EDIT_ADDRESSING_PERMISSION,
        read_permission=ModifyPortalContent,
        validators=('isEmail',),
        widget=StringWidget(
            label = _(u'label_formmailer_recipient_email',
                      default=u"Recipient's e-mail address"),
            description = _(u'help_formmailer_recipient_email',
                            default=u'The recipients e-mail address.'),
            ),
        ),
    StringField('to_field',
        schemata='addressing',
        searchable=0,
        required=0,
        default='#NONE#',
        write_permission=EDIT_ADVANCED_PERMISSION,
        read_permission=ModifyPortalContent,
        vocabulary='fieldsDisplayList',
        widget=SelectionWidget(
            label = _(u'label_formmailer_to_extract', default=u'Extract Recipient From'),
            description = _(u'help_formmailer_to_extract', default=\
                u"""
                Choose a form field from which you wish to extract
                input for the To header. If you choose anything other
                than "None", this will override the "Recipient's e-mail address"
                setting above. Be very cautious about allowing unguarded user
                input for this purpose.
                """),
            ),
        ),
    LinesField('cc_recipients',
        searchable=0,
        required=0,
        default_method='getDefaultCC',
        schemata='addressing',
        write_permission=EDIT_ADDRESSING_PERMISSION,
        read_permission=ModifyPortalContent,
        widget=LinesWidget(
            label = _(u'label_formmailer_cc_recipients',
                      default=u'CC Recipients'),
            description = _(u'help_formmailer_cc_recipients',
                    default=u'E-mail addresses which receive a carbon copy.'),
            ),
        ),
    LinesField('bcc_recipients',
        schemata='addressing',
        searchable=0,
        required=0,
        default_method='getDefaultBCC',
        write_permission=EDIT_ADDRESSING_PERMISSION,
        read_permission=ModifyPortalContent,
        widget=LinesWidget(
            label = _(u'label_formmailer_bcc_recipients',
                      default=u'BCC Recipients'),
            description = _(u'help_formmailer_bcc_recipients',
                default=u'E-mail addresses which receive a blind carbon copy.'),
            ),
        ),
    StringField('replyto_field',
        schemata='addressing',
        searchable=0,
        required=0,
        vocabulary='fieldsDisplayList',
        read_permission=ModifyPortalContent,
        write_permission=EDIT_ADVANCED_PERMISSION,
        widget=SelectionWidget(
            label = _(u'label_formmailer_replyto_extract',
                      default=u'Extract Reply-To From'),
            description = _(u'help_formmailer_replyto_extract', default=\
                u"""
                Choose a form field from which you wish to extract
                input for the Reply-To header. NOTE: You should
                activate e-mail address verification for the designated
                field.
                """),
            ),
        ),
    StringField('msg_subject',
        schemata='message',
        searchable=0,
        required=0,
        default='Form Submission',
        read_permission=ModifyPortalContent,
        widget=StringWidget(
            description = _(u'help_formmailer_subject', default=
                u"""
                Subject line of message. This is used if you
                do not specify a subject field or if the field
                is empty.
                """),
            label = _(u'label_formmailer_subject', default=u'Subject'),
            ),
        ),
    StringField('subject_field',
        schemata='message',
        searchable=0,
        required=0,
        vocabulary='fieldsDisplayList',
        write_permission=EDIT_ADVANCED_PERMISSION,
        read_permission=ModifyPortalContent,
        widget=SelectionWidget(
            label = _(u'label_formmailer_subject_extract',
                      default=u'Extract Subject From'),
            description = _(u'help_formmailer_subject_extract', default=\
                u"""
                Choose a form field from which you wish to extract
                input for the mail subject line.
                """),
            ),
        ),
    TextField('body_pre',
        searchable=0,
        required=0,
        schemata='message',
        accessor='getBody_pre',
        read_permission=ModifyPortalContent,
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget(description = _(u'help_formmailer_body_pre',
                      default=u'Text prepended to fields listed in mail-body'),
          label = _(u'label_formmailer_body_pre', default=u'Body (prepended)'),
            ),
        ),
    TextField('body_post',
        searchable=0,
        required=0,
        schemata='message',
        read_permission=ModifyPortalContent,
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget(description = _(u'help_formmailer_body_post',
                      default=u'Text appended to fields listed in mail-body'),
          label = _(u'label_formmailer_body_post', default=u'Body (appended)'),
            ),
        ),

    TextField('body_footer',
        searchable=0,
        required=0,
        schemata='message',
        read_permission=ModifyPortalContent,
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget(description = _(u'help_formmailer_body_footer',
                          default=u'Text used as the footer at '
                          u'bottom, delimited from the body by a dashed line.'),
            label = _(u'label_formmailer_body_footer',
                      default=u'Body (signature)'),
            ),
        ),
    BooleanField('showAll',
        required=0,
        searchable=0,
        schemata='message',
        default='1',
        widget=BooleanWidget(
            label=_(u'label_mailallfields_text', default=u"Include All Fields"),
            description=_(u'help_mailallfields_text', default=u"""
                Check this to include input for all fields
                (except label and file fields). If you check
                this, the choices in the pick box below
                will be ignored.
                """),
            ),
        ),
    LinesField('showFields',
        required=0,
        searchable=0,
        schemata='message',
        vocabulary='allFieldDisplayList',
        widget=PicklistWidget(
            label=_(u'label_mailfields_text', default=u"Show Responses"),
            description=_(u'help_mailfields_text', default=u"""
                Pick the fields whose inputs you'd like to include in
                the e-mail.
                """),
            ),
        ),
    BooleanField('includeEmpties',
        required=0,
        searchable=0,
        schemata='message',
        default='1',
        widget=BooleanWidget(
            label=_(u'label_mailEmpties_text', default=u"Include Empties"),
            description=_(u'help_mailEmpties_text', default=u"""
                Check this to include titles
                for fields that received no input. Uncheck
                to leave fields with no input out of the e-mail.
                """),
            ),
        ),
    ZPTField('body_pt',
        schemata='template',
        write_permission=EDIT_TALES_PERMISSION,
        default_method = 'getMailBodyDefault',
        read_permission=ModifyPortalContent,
        widget=TextAreaWidget(description = _(u'help_formmailer_body_pt',
            default=u"""This is a Zope Page Template
            used for rendering of the mail-body. You don\'t need to modify 
            it, but if you know TAL (Zope\'s Template Attribute Language) 
            you have the full power to customize your outgoing mails."""),
            label = _(u'label_formmailer_body_pt', default=u'Mail-Body Template'),
            rows = 20,
            visible = {'edit':'visible','view':'invisible'},
            ) ,
        validators=('zptvalidator',),
        ),
    StringField('body_type',
        schemata='template',
        default_method='getMailBodyTypeDefault',
        vocabulary = MIME_LIST,
        write_permission=EDIT_ADVANCED_PERMISSION,
        read_permission=ModifyPortalContent,
        widget=SelectionWidget(description = _(u'help_formmailer_body_type',
            default=u"""Set the mime-type of the mail-body. 
            Change this setting only if you know exactly what you are doing. 
            Leave it blank for default behaviour."""),
            label = _(u'label_formmailer_body_type', default=u'Mail-Body Type'),
            ),
        ),
    LinesField('xinfo_headers',
        searchable=0,
        required=0,
        schemata='headers',
        default_method='getDefaultXInfo',
        write_permission=EDIT_ADVANCED_PERMISSION,
        read_permission=ModifyPortalContent,
        vocabulary=DisplayList( (
            ('HTTP_X_FORWARDED_FOR','HTTP_X_FORWARDED_FOR',),
            ('REMOTE_ADDR','REMOTE_ADDR',),
            ('PATH_INFO', 'PATH_INFO'),
            ('HTTP_USER_AGENT','HTTP_USER_AGENT',),
            ('HTTP_REFERER', 'HTTP_REFERER'),
            ), ),
        widget=MultiSelectionWidget(
            label=_(u'label_xinfo_headers_text', default=u'HTTP Headers'),
            description=_(u'help_xinfo_headers_text', default=u"""
                Pick any items from the HTTP headers that
                you'd like to insert as X- headers in the
                message.
                """),
            format='checkbox',
            ),
        ),
    LinesField('additional_headers',
        schemata='headers',
        searchable=0,
        required=0,
        default_method='getDefaultAddHdrs',
        write_permission=EDIT_ADVANCED_PERMISSION,
        read_permission=ModifyPortalContent,
        widget=LinesWidget(
            label = _(u'label_formmailer_additional_headers',default=u'Additional Headers'),
            description=_(u'help_formmailer_additional_headers', default=u"""
                Additional e-mail-header lines.
                Only use RFC822-compliant headers.
                """),
            ),
        ),
))

if gpg is not None:
    formMailerAdapterSchema = formMailerAdapterSchema + Schema((
        StringField('gpg_keyid',
            schemata='encryption',
            accessor='getGPGKeyId',
            mutator='setGPGKeyId',
            write_permission=USE_ENCRYPTION_PERMISSION,
            read_permission=ModifyPortalContent,
            widget=StringWidget(
                description = _(u'help_gpg_key_id',default=u"""
                    Give your key-id, e-mail address or
                    whatever works to match a public key from current keyring.
                    It will be used to encrypt the message body.
                    Contact the site administrator if you need to
                    install a new public key.
                    Note that you will probably wish to change your message
                    template to plain text if you're using encryption.
                    TEST THIS FEATURE BEFORE GOING PUBLIC!
                    """),
                label = _(u'label_gpg_key_id', default=u'Key-Id'),
                ),
            ),
        ))


formMailerAdapterSchema = formMailerAdapterSchema + Schema((
    TALESString('subjectOverride',
        schemata='overrides',
        searchable=0,
        required=0,
        validators=('talesvalidator',),
        default='',
        write_permission=EDIT_TALES_PERMISSION,
        read_permission=ModifyPortalContent,
        isMetadata=True, # just to hide from base view
        widget=StringWidget(label=_(u'label_subject_override_text', default=u"Subject Expression"),
            description=_(u'help_subject_override_text', default=u"""
                A TALES expression that will be evaluated to override any value
                otherwise entered for the e-mail subject header.
                Leave empty if unneeded. Your expression should evaluate as a string.
                PLEASE NOTE: errors in the evaluation of this expression will cause
                an error on form display.
            """),
            size=70,
        ),
    ),
    TALESString('senderOverride',
        schemata='overrides',
        searchable=0,
        required=0,
        validators=('talesvalidator',),
        default='',
        write_permission=EDIT_TALES_PERMISSION,
        read_permission=ModifyPortalContent,
        isMetadata=True, # just to hide from base view
        widget=StringWidget(label=_(u'label_sender_override_text',
                                    default=u"Sender Expression"),
            description=_(u'help_sender_override_text', default=u"""
                A TALES expression that will be evaluated to override the "From" header.
                Leave empty if unneeded. Your expression should evaluate as a string.
                PLEASE NOTE: errors in the evaluation of this expression will cause
                an error on form display.
            """),
            size=70,
        ),
    ),
    TALESString('recipientOverride',
        schemata='overrides',
        searchable=0,
        required=0,
        validators=('talesvalidator',),
        default='',
        write_permission=EDIT_TALES_PERMISSION,
        read_permission=ModifyPortalContent,
        isMetadata=True, # just to hide from base view
        widget=StringWidget(label=_(u'label_recipient_override_text', default=u"Recipient Expression"),
            description=_(u'help_recipient_override_text', default=u"""
                A TALES expression that will be evaluated to override any value
                otherwise entered for the recipient e-mail address. You are strongly
                cautioned against using unvalidated data from the request for this purpose.
                Leave empty if unneeded. Your expression should evaluate as a string.
                PLEASE NOTE: errors in the evaluation of this expression will cause
                an error on form display.
            """),
            size=70,
        ),
    ),
    TALESString('bccOverride',
        schemata='overrides',
        searchable=0,
        required=0,
        validators=('talesvalidator',),
        default='',
        write_permission=EDIT_TALES_PERMISSION,
        read_permission=ModifyPortalContent,
        isMetadata=True, # just to hide from base view
        widget=StringWidget(label=_(u'label_bcc_override_text', default=u"BCC Expression"),
            description=_(u'help_bcc_override_text', default=u"""
                A TALES expression that will be evaluated to override any value
                otherwise entered for the BCC list. You are strongly
                cautioned against using unvalidated data from the request for this purpose.
                Leave empty if unneeded. Your expression should evaluate as a sequence of strings.
                PLEASE NOTE: errors in the evaluation of this expression will cause
                an error on form display.
            """),
            size=70,
        ),
    ),
))

# move headers schema items to template schema to keep the schema
# count <= 6
formMailerAdapterSchema['xinfo_headers'].schemata = 'template'
formMailerAdapterSchema['additional_headers'].schemata = 'template'

formMailerAdapterSchema.moveField('execCondition', pos='bottom')


class FormMailerAdapter(FormActionAdapter):
    """ A form action adapter that will e-mail form input. """

    schema = formMailerAdapterSchema
    portal_type = meta_type = 'FormMailerAdapter'
    archetype_name = 'Mailer Adapter'
    content_icon = 'mailaction.gif'

    security       = ClassSecurityInfo()


    def initializeArchetype(self, **kwargs):
        """ Translate the adapter in the current langage
        """

        FormActionAdapter.initializeArchetype(self, **kwargs)

        self.setMsg_subject(zope.i18n.translate(_(u'pfg_formmaileradapter_msg_subject', u'Form Submission'), context=self.REQUEST))


    security.declarePrivate('onSuccess')
    def onSuccess(self, fields, REQUEST=None):
        """
        e-mails data.
        """

        self.send_form(fields, REQUEST)


    security.declarePrivate('getMailBodyDefault')
    def getMailBodyDefault(self):
        """ Get default mail body from our tool """

        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getDefaultMailTemplateBody()


    security.declarePrivate('getMailBodyTypeDefault')
    def getMailBodyTypeDefault(self):
        """ Get default mail body type from our tool """

        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getDefaultMailBodyType()


    security.declarePrivate('getDefaultRecipient')
    def getDefaultRecipient(self):
        """ Get default mail recipient from our tool """

        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getDefaultMailRecipient()


    security.declarePrivate('getDefaultRecipientName')
    def getDefaultRecipientName(self):
        """ Get default mail recipient from our tool """

        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getDefaultMailRecipientName()


    security.declarePrivate('getDefaultCC')
    def getDefaultCC(self):
        """ Get default mail cc from our tool """

        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getDefaultMailCC()


    security.declarePrivate('getDefaultBCC')
    def getDefaultBCC(self):
        """ Get default mail bcc from our tool """

        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getDefaultMailBCC()


    security.declarePrivate('getDefaultXInfo')
    def getDefaultXInfo(self):
        """ Get default mail xinfo hdrs from our tool """

        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getDefaultMailXInfo()


    security.declarePrivate('getDefaultAddHdrs')
    def getDefaultAddHdrs(self):
        """ Get default mail add headers from our tool """

        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getDefaultMailAddHdrs()


    security.declarePublic('setBody_pt')
    def setBody_pt(self, value, **kw):
        """ set body template with BBB for accessors """
        
        if shasattr(value, 'replace'):
            template = value
            for s, t in [('body_pre', 'getBody_pre'),
                         ('body_post', 'getBody_post'), 
                         ('body_footer', 'getBody_footer')]:
                template = template.replace('here/%s' % s, 'here/%s' % t)
            myField = self.getField('body_pt')
            myField.set(self, template)


    security.declarePrivate('_dreplace')
    def _dreplace(self, s):
        return dollarReplace.DollarVarReplacer(getattr(self.REQUEST, 'form', {})).sub(s)


    security.declarePublic('getBody_pre')
    def getBody_pre(self):
        """ get expanded mail body prefix """
        
        return self._dreplace( self.getRawBody_pre() )


    security.declarePublic('getBody_post')
    def getBody_post(self):
        """ get expanded mail body postfix """

        return self._dreplace( self.getRawBody_post() )


    security.declarePublic('getBody_footer')
    def getBody_footer(self):
        """ get expanded mail body footer """

        return self._dreplace( self.getRawBody_footer() )


    security.declarePrivate('get_mail_text')
    def get_mail_text(self, fields, request, **kwargs):
        """Get header and body of e-mail as text (string)
        """
        
        (headerinfo, additional_headers,
         body) = self.get_header_body_tuple(fields, request, **kwargs)

        if not isinstance(body, unicode):
            body = unicode(body, self._site_encoding())
        portal = getToolByName(self, 'portal_url').getPortalObject()
        email_charset = portal.getProperty('email_charset', 'utf-8')
        mime_text = MIMEText(body.encode(email_charset , 'replace'),
                _subtype=self.body_type or 'html', _charset=email_charset)

        attachments = self.get_attachments(fields, request)

        if attachments:
            outer = MIMEMultipart()
            outer.attach(mime_text)
        else:
            outer = mime_text

        # write header
        for key, value in headerinfo.items():
            outer[key] = value

        # write additional header
        for a in additional_headers:
            key, value = a.split(':', 1)
            outer.add_header(key, value.strip())

        for attachment in attachments:
            filename = attachment[0]
            ctype = attachment[1]
            encoding = attachment[2]
            content = attachment[3]

            if ctype is None:
                ctype = 'application/octet-stream'

            maintype, subtype = ctype.split('/', 1)

            if maintype == 'text':
                msg = MIMEText(content, _subtype=subtype)
            elif maintype == 'image':
                msg = MIMEImage(content, _subtype=subtype)
            elif maintype == 'audio':
                msg = MIMEAudio(content, _subtype=subtype)
            else:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(content)
                # Encode the payload using Base64
                Encoders.encode_base64(msg)

            # Set the filename parameter
            msg.add_header('Content-Disposition', 'attachment', filename=filename)
            outer.attach(msg)

        return outer.as_string()


    def get_attachments(self, fields, request):
        """Return all attachments uploaded in form.
        """

        from ZPublisher.HTTPRequest import FileUpload

        attachments = []

        for field in fields:
            if field.isFileField() and (getattr(self, 'showAll', True) \
                or field.fgField.getName() in getattr(self, 'showFields', ())):
                file = request.form.get('%s_file' % field.__name__, None)
                if file and isinstance(file, FileUpload) and file.filename != '':
                    file.seek(0) # rewind
                    data = file.read()
                    filename = file.filename
                    mimetype, enc = guess_content_type(filename, data, None)
                    attachments.append((filename, mimetype, enc, data))
        return attachments

    security.declarePrivate('get_mail_body')
    def get_mail_body(self, fields, **kwargs):
        """Returns the mail-body with footer.
        """

        if kwargs.has_key('request'):
            request = kwargs['request']
        else:
            request = self.REQUEST

        all_fields = [f for f in fields
            if not (f.isLabel() or f.isFileField()) and not (getattr(self, 'showAll', True) and f.getServerSide())]

        # which fields should we show?
        if getattr(self, 'showAll', True):
            live_fields = all_fields 
        else:
            live_fields = \
                [f for f in all_fields
                   if f.fgField.getName() in getattr(self, 'showFields', ())]

        if not getattr(self, 'includeEmpties', True):
            all_fields = live_fields
            live_fields = []
            for f in all_fields:
                value = f.htmlValue(request)
                if value and value != 'No Input':
                    live_fields.append(f)
                
        bare_fields = [f.fgField for f in live_fields]
        bodyfield = self.getField('body_pt')
        
        # pass both the bare_fields (fgFields only) and full fields.
        # bare_fields for compatability with older templates,
        # full fields to enable access to htmlValue
        body = bodyfield.get(self, fields=bare_fields, wrappedFields=live_fields,**kwargs)

        if isinstance(body, unicode):
            body = body.encode(self.getCharset())

        keyid = getattr(self, 'gpg_keyid', None)
        encryption = gpg and keyid

        if encryption:
            bodygpg = gpg.encrypt(body, keyid)
            if bodygpg.strip():
                body = bodygpg

        return body


    security.declarePrivate('secure_header_line')
    def secure_header_line(self, line):
        nlpos = line.find('\x0a')
        if nlpos >= 0:
            line = line[:nlpos]
        nlpos = line.find('\x0d')
        if nlpos >= 0:
            line = line[:nlpos]
        return line


    security.declarePrivate('_destFormat')
    def _destFormat(self, input):
        """ Format destination (To) input.
            Input may be a string or sequence of strings;
            returns a well-formatted address field
        """

        if type(input) in StringTypes:
            input = [s for s in input.split(',')]
        input = [s for s in input if s]
        filtered_input = [s.strip().encode('utf-8') for s in input]
        
        if filtered_input:        
            return "<%s>" % '>, <'.join( filtered_input )
        else:
            return ''


    security.declarePrivate('get_header_body_tuple')
    def get_header_body_tuple(self, fields, request,
                              from_addr=None, to_addr=None,
                              subject=None, **kwargs):
        """Return header and body of e-mail as an 3-tuple:
        (header, additional_header, body)

        header is a dictionary, additional header is a list, body is a StringIO

        Keyword arguments:
        request -- (optional) alternate request object to use
        """

        pprops = getToolByName(self, 'portal_properties')
        site_props = getToolByName(pprops, 'site_properties')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        pms = getToolByName(self, 'portal_membership')
        utils = getToolByName(self, 'plone_utils')
        
        body = self.get_mail_body(fields, **kwargs)

        # fields = self.fgFields()

        # get Reply-To
        reply_addr = None
        if shasattr(self, 'replyto_field'):
            reply_addr = request.form.get(self.replyto_field, None)

        # get subject header
        nosubject = '(no subject)'
        if shasattr(self, 'subjectOverride') and self.getRawSubjectOverride():
            # subject has a TALES override
            subject = self.getSubjectOverride().strip()
        else:
            subject = getattr(self, 'msg_subject', nosubject)
            subjectField = request.form.get(self.subject_field, None)
            if subjectField is not None:
                subject = subjectField
            else:
                # we only do subject expansion if there's no field chosen
                subject = self._dreplace(subject)

        # Get From address
        if shasattr(self, 'senderOverride') and self.getRawSenderOverride():
            from_addr = self.getSenderOverride().strip()
        else:
            from_addr = from_addr or site_props.getProperty('email_from_address') or \
                        portal.getProperty('email_from_address')

        # Get To address and full name
        if shasattr(self, 'recipientOverride') and self.getRawRecipientOverride():
            recip_email = self.getRecipientOverride()
        else:
            recip_email = None
            if shasattr(self, 'to_field'):
                recip_email = request.form.get(self.to_field, None)
            if not recip_email:
                recip_email = self.recipient_email
        recip_email = self._destFormat( recip_email )

        recip_name = self.recipient_name.encode('utf-8')

        # if no to_addr and no recip_email specified, use owner adress if possible.
        # if not, fall back to portal email_from_address.
        # if still no destination, raise an assertion exception.
        if not recip_email and not to_addr:
            ownerinfo = self.getOwner()
            ownerid=ownerinfo.getId()
            userdest = pms.getMemberById(ownerid)
            toemail = ''
            if userdest is not None:
                toemail = userdest.getProperty('email', '')
            if not toemail:
                toemail = portal.getProperty('email_from_address')                
            assert toemail, """
                    Unable to mail form input because no recipient address has been specified.
                    Please check the recipient settings of the PloneFormGen "Mailer" within the
                    current form folder.
                """
            to = '%s <%s>' %(ownerid,toemail)
        else:
            to = to_addr or '%s %s' % (recip_name, recip_email)

        headerinfo = OrderedDict()

        headerinfo['To'] = self.secure_header_line(to)
        headerinfo['From'] = self.secure_header_line(from_addr)
        if reply_addr:
            headerinfo['Reply-To'] = self.secure_header_line(reply_addr)

        # transform subject into mail header encoded string
        email_charset = portal.getProperty('email_charset', 'utf-8')

        if not isinstance(subject, unicode):
            site_charset = utils.getSiteEncoding()            
            subject = unicode(subject, site_charset, 'replace')        
        
        msgSubject = self.secure_header_line(subject).encode(email_charset, 'replace')
        msgSubject = str(Header(msgSubject, email_charset))
        headerinfo['Subject'] = msgSubject

        headerinfo['MIME-Version'] = '1.0'

        # CC
        cc_recips = filter(None, self.cc_recipients)
        if cc_recips:
            headerinfo['Cc'] = self._destFormat( cc_recips )

        # BCC
        bcc_recips = filter(None, self.bcc_recipients)
        if shasattr(self, 'bccOverride') and self.getRawBccOverride():
            bcc_recips = self.getBccOverride()
        if bcc_recips:
            headerinfo['Bcc'] = self._destFormat( bcc_recips )

        for key in getattr(self, 'xinfo_headers', []):
            headerinfo['X-%s' % key] = self.secure_header_line(request.get(key, 'MISSING'))

        # return 3-Tuple
        return (headerinfo, self.additional_headers, body)


    def send_form(self, fields, request, **kwargs):
        """Send the form.
        """

        mailtext=self.get_mail_text(fields, request, **kwargs)
        host = self.MailHost
        host.send(mailtext)


    # translation and encodings
    def _site_encoding(self):
        site_props = self.portal_properties.site_properties
        return site_props.default_charset or 'UTF-8'


    security.declareProtected(View, 'allFieldDisplayList')
    def allFieldDisplayList(self):
        """ returns a DisplayList of all fields """

        return self.fgFieldsDisplayList()


    def fieldsDisplayList(self):
        """ returns display list of fields with simple values """

        return self.fgFieldsDisplayList(
            withNone=True,
            noneValue='#NONE#',
            objTypes=(
                'FormSelectionField',
                'FormStringField',
                )
            )


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


registerATCT(FormMailerAdapter, PROJECTNAME)
