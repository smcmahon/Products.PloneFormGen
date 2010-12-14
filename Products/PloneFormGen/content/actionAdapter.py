"""actionAdapter -- A base adapter for form actions"""

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

import re

from zope.interface import implements
import transaction
import zExceptions
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.Archetypes.public import *
from Products.Archetypes.utils import shasattr

from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT

from Products.TALESField import TALESString

from Products.PloneFormGen import PloneFormGenMessageFactory as _
from Products.PloneFormGen.config import *
from Products.PloneFormGen.interfaces import IPloneFormGenActionAdapter

FormAdapterSchema = ATContentTypeSchema.copy() + Schema((
    TALESString('execCondition',
        schemata='overrides',
        searchable=0,
        required=0,
        validators=('talesvalidator',),
        default='',
        write_permission=EDIT_TALES_PERMISSION,
        read_permission=ModifyPortalContent,
        isMetadata=True, # just to hide from base view
        widget=StringWidget(label=_(u'label_execcondition_text', default=u"Execution Condition"),
            description=_(u'help_execcondition_text', default=u"""
                A TALES expression that will be evaluated to determine whether or not
                to execute this action.
                Leave empty if unneeded, and the action will be executed. 
                Your expression should evaluate as a boolean; return True if you wish
                the action to execute.
                PLEASE NOTE: errors in the evaluation of this expression will cause
                an error on form display.
            """),
            size=70,
        ),
    ),
    ))

finalizeATCTSchema(FormAdapterSchema, folderish=True, moveDiscussion=False)

# avoid showing unnecessary schema tabs
for afield in ('description',
               'subject', 
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
    FormAdapterSchema[afield].widget.visible = {'view':'invisible','edit':'invisible'}
    FormAdapterSchema[afield].schemata = 'default'


class FormActionAdapter(ATCTContent):
    """A base action adapter"""

    implements(IPloneFormGenActionAdapter)

    schema         =  FormAdapterSchema

    content_icon   = 'FormAction.gif'
    meta_type      = 'FormActionAdapter'
    portal_type    = 'FormActionAdapter'
    archetype_name = 'Form Action Adapter'

    immediate_view = 'base_view'
    default_view   = 'base_view'
    suppl_views = ()

    typeDescription= 'An adapter that supplies a form action.'

    global_allow = 0    

    security       = ClassSecurityInfo()


    def onSuccess(self, fields, REQUEST=None):
        """ Called by form to invoke custom success processing.
            return None (or don't use "return" at all) if processing is
            error-free.
            
            Return a dictionary like {'field_id':'Error Message'}
            and PFG will stop processing action adapters and
            return back to the form to display your error messages
            for the matching field(s).

            You may also use Products.PloneFormGen.config.FORM_ERROR_MARKER
            as a marker for a message to replace the top-of-the-form error
            message.

            For example, to set a message for the whole form, but not an
            individual field:

            {FORM_ERROR_MARKER:'Yuck! You will need to submit again.'}

            For both a field and form error:

            {FORM_ERROR_MARKER:'Yuck! You will need to submit again.',
             'field_id':'Error Message for field.'}
            
            Messages may be string types or zope.i18nmessageid objects.                
        """
        
        # fields will be a sequence of objects with an IPloneFormGenField interface
        
        pass


    def at_post_create_script(self):
        """ activate action adapter in parent folder """
        
        # XXX TODO - change to use events when we give up on Plone 2.1.x
        
        ATCTContent.at_post_create_script(self)

        self.aq_parent.addActionAdapter(self.id)
