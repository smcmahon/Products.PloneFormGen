###etc move the schemata out of form.py because it is a big enough file already!
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.ATContentTypes.configuration import zconf
from Products.TALESField import TALESString
from Products.PloneFormGen.config import \
    EDIT_TALES_PERMISSION, EDIT_ADVANCED_PERMISSION, BAD_IDS, FORM_ERROR_MARKER

try:
    from Products.LinguaPlone.public import *
except ImportError:
    from Products.Archetypes.public import *


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
                form submit. (If none are available, add one.) Choose none to simply display the form
                field values.
            """,
            description_msgid = "help_thankspage_text",
            i18n_domain = "ploneformgen",
            ),
        ),
    TextField('formPrologue',
        schemata='decoration',
        required=False,
        # Disable search to bypass a unicode decode error in portal_catalog indexes.
        searchable=False,
        primary=False,
        validators = ('isTidyHtmlWithCleanup',),
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
        # Disable search to bypass a unicode decode error in portal_catalog indexes.
        searchable=False,
        primary=False,
        validators = ('isTidyHtmlWithCleanup',),
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
                your action adapter (if you have one). You would usually use this for a custom
                success template or script.
                Leave empty if unneeded. Otherwise, specify as you would a CMFFormController
                action type and argument,
                complete with type of action to execute (e.g., "redirect_to" or "traverse_to")
                and a TALES expression. For example, "redirect_to:string:thanks-page" would
                redirect to 'thanks-page'.
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
        validators='isURL',
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
        validators=('talesvalidator',),
        write_permission=EDIT_TALES_PERMISSION,
        default='',
        languageIndependent=1,
        widget=StringWidget(label="Form Setup Script",
            description="""
                A TALES expression that will be called when the form is displayed.
                Leave empty if unneeded.
                The most common use of this field is to call a python script that sets
                defaults for multiple fields by pre-populating request.form.
                Any value returned by the expression is ignored.
                PLEASE NOTE: errors in the evaluation of this expression will cause
                an error on form display.
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
        validators=('talesvalidator',),
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
                PLEASE NOTE: errors in the evaluation of this expression will cause
                an error on form display.
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
        validators=('talesvalidator',),
        write_permission=EDIT_TALES_PERMISSION,
        default='',
        languageIndependent=1,
        widget=StringWidget(label="Header Injection",
            description="""
                This override field allows you to insert content into the xhtml
                head. The typical use is to add custom CSS or JavaScript.
                Specify a TALES expression returning a string. The string will
                be inserted with no interpretation.
                PLEASE NOTE: errors in the evaluation of this expression will cause
                an error on form display.
            """,
            size=70,
            i18n_domain = "ploneformgen",
            label_msgid = "label_headerInjection_text",
            description_msgid = "help_headerInjection_text",
            ),
        ),
    ))
