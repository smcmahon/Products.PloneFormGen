"""config -- shared values"""

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.public import DisplayList
from Products.validation.validators.BaseValidators import protocols, EMAIL_RE


############################################
### Things you might customize for your site

DEFAULT_MAILTEMPLATE_BODY = \
"""<html xmlns="http://www.w3.org/1999/xhtml">

  <head><title></title></head>

  <body>
    <p tal:content="here/getBody_pre | nothing" />
    <dl>
        <tal:block repeat="field options/wrappedFields | nothing">
            <dt tal:content="field/fgField/widget/label" />
            <dd tal:content="structure python:field.htmlValue(request)" />
        </tal:block>
    </dl>
    <p tal:content="here/getBody_post | nothing" />
    <pre tal:content="here/getBody_footer | nothing" />
  </body>
</html>
"""

MIME_LIST = DisplayList(
    (('html', 'HTML'),
     ('plain', 'Text'),
     ))

XINFO_DEFAULT = ['HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR', 'PATH_INFO']

## Customizable String Validators
#
#  These are used by the String Form Field.
#
#  All are built from a regular expression and an
#  ignore string.
#
#  Note that in Plone 2.5+, i18n messageids will
#  be constructed from the i18nid/title and errmsg/errid
#  pairs. So, these are fully translatable.

stringValidators = (
    {'id':'isEmail',
        'i18nid':'vocabulary_isemailaddress_text',
        'title':u'Is an E-Mail Address',
        'errmsg':u'This is not a valid email address.',
        'errid':'pfg_isEmail',
        'regex':'^'+EMAIL_RE,
        'ignore':'',
        },
    {'id':'isCommaSeparatedEmails',
        'i18nid':'vocabulary_isemailaddresslist_text',
        'title':u'Is one or more E-Mail Addresses separated by commas',
        'errmsg':u'This is not a valid list of email addresses (separated by commas).',
        'errid':'pfg_isEmailAddressList',
        'regex':r'^'+EMAIL_RE[:-1]+'(,\s*'+EMAIL_RE[:-1]+')*$',
        'ignore':'',
        },
    {'id':'isPrintable',
        'i18nid':'vocabulary_onlyprintable_text',
        'title':u'Contains only printable characters',
        'errmsg':u'This value contains unprintable characters.',
        'errid':'pfg_isPrintable',
        'regex':r'[a-zA-Z0-9\s]+$',
        'ignore':'',
    },
    {'id':'isURL',
        'i18nid':'vocabulary_isurl_text',
        'title':u'Is a well-formed URL',
        'errmsg':u'This is not a valid url.',
        'errid':'pfg_isURL',
        'regex':r'(%s)s?://[^\s\r\n]+' % '|'.join(protocols),
        'ignore':'',
    },
    {'id':'isUSPhoneNumber',
        'i18nid':'vocabulary_isusphone_text',
        'title':u'Is a valid US phone number',
        'errmsg':u'This is not a valid us phone number.',
        'errid':'pfg_isUSPhoneNumber',
        'regex':r'^\d{10}$',
        'ignore':'[\(\)\-\s]',
    },
    {'id':'isInternationalPhoneNumber',
        'i18nid':'vocabulary_isintphone_text',
        'title':u'Is a valid international phone number',
        'errmsg':u'This is not a valid international phone number.',
        'errid':'pfg_isInternationalPhoneNumber',
        'regex':r'^\d+$',
        'ignore':'[\(\)\-\s\+]',
    },
    {'id':'isZipCode',
        'i18nid':'vocabulary_iszipcode_text',
        'title':u'Is a valid postal code',
        'errmsg':u'This is not a valid postal code.',
        'errid':'pfg_isZipCode',
        'regex':r'^\d{5}(\d{4})?$|^[ABCEGHJKLMNPRSTVXYabceghjklmnprstvxy]{1}\d{1}[A-Za-z]{1}\d{1}[A-Za-z]{1}\d{1}$',
        'ignore':'[\- ]',
    },
    {'id': 'isNotLinkSpam',
        'i18nid':'vocabulary_isnotlinkspam_text',
        'title':u'Does not contain link spam',
        'errmsg':u'This text appears to contain links.',
        'errid':'pfg_isnotlinkspam',
        'regex':r'(?!(<a |http|www|\.com)).*',
        'ignore':'',
    }
)


######
# Extra content types allowed inside form folders

EXTRA_ALLOWED = ['Document', 'Image', 'FieldsetStart', 'FieldsetEnd']

######
# LinguaPlone-related settings

# Set this True to cause SaveData action adapters in translated forms to save
# to the matching SaveData adapter in the canonical version (if there is one).
LP_SAVE_TO_CANONICAL = True


### End of likely customizations
### Change anything below and things are likely to break
########################################################


## The Project Name
PROJECTNAME = "PloneFormGen"

## The skins dir
SKINS_DIR = 'skins'

# property sheet (in portal_properties)
PROPERTY_SHEET_NAME = 'ploneformgen_properties'

## Globals variable
GLOBALS = globals()

fieldTypes = (
    'FormSelectionField',
    'FormMultiSelectionField',
    'FormLabelField',
    'FormDateField',
    'FormLinesField',
    'FormIntegerField',
    'FormBooleanField',
    'FormPasswordField',
    'FormFixedPointField',
    'FormStringField',
    'FormTextField',
    'FormRichTextField',
    'FormRichLabelField',
    'FormFileField',
    'FormLikertField',
    'FormCaptchaField',
)

adapterTypes = (
    'FormSaveDataAdapter',
    'FormMailerAdapter',
    'FormCustomScriptAdapter',    
)

thanksTypes = (
    'FormThanksPage',
)

fieldsetTypes = (
    'FieldsetFolder',
)

## Permission for content creation for most types
ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Content'
setDefaultRoles(ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Contributor', 'Site Administrator'))

## Exceptions
MA_ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Mailers'
setDefaultRoles(MA_ADD_CONTENT_PERMISSION, ('Manager','Owner','Site Administrator'))
SDA_ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Data Savers'
setDefaultRoles(SDA_ADD_CONTENT_PERMISSION, ('Manager','Owner','Site Administrator'))
CSA_ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Custom Scripts'
setDefaultRoles(CSA_ADD_CONTENT_PERMISSION, ('Manager',))

## Permission to use TALESField, ZPTField
EDIT_TALES_PERMISSION = 'PloneFormGen: Edit TALES Fields'
setDefaultRoles(EDIT_TALES_PERMISSION, ('Manager',))

## Permission to use TALESField, ZPTField
EDIT_PYTHON_PERMISSION = 'PloneFormGen: Edit Python Fields'
setDefaultRoles(EDIT_PYTHON_PERMISSION, ('Manager',))

## Permission to use advanced fields
EDIT_ADVANCED_PERMISSION = 'PloneFormGen: Edit Advanced Fields'
setDefaultRoles(EDIT_ADVANCED_PERMISSION, ('Manager','Site Administrator'))

## Permission to use mail adapter addressing fields
EDIT_ADDRESSING_PERMISSION = 'PloneFormGen: Edit Mail Addresses'
setDefaultRoles(EDIT_ADDRESSING_PERMISSION, ('Manager','Owner','Site Administrator'))

## Permission to use encryption fields
USE_ENCRYPTION_PERMISSION = 'PloneFormGen: Edit Encryption Specs'
setDefaultRoles(USE_ENCRYPTION_PERMISSION, ('Manager',))

## Permission to download saved data
DOWNLOAD_SAVED_PERMISSION = 'PloneFormGen: Download Saved Input'
setDefaultRoles(DOWNLOAD_SAVED_PERMISSION, ('Manager', 'Owner', 'Site Administrator'))

## Our list of permissions
pfgPermitList = [
    ADD_CONTENT_PERMISSION,
    MA_ADD_CONTENT_PERMISSION,
    SDA_ADD_CONTENT_PERMISSION,
    CSA_ADD_CONTENT_PERMISSION,
    EDIT_TALES_PERMISSION,
    EDIT_PYTHON_PERMISSION,
    EDIT_ADVANCED_PERMISSION,
    EDIT_ADDRESSING_PERMISSION,
    USE_ENCRYPTION_PERMISSION,
    DOWNLOAD_SAVED_PERMISSION,
]

## Some object ids allowed by Plone can cause lots of trouble
#  if they're used for PFG field elements.
#  The disallow list:
BAD_IDS = ('zip', 'location', 'language')

# used to mark errors that belong to the
# whole form, not just a field.
FORM_ERROR_MARKER = '_pfg_form_error'

# apply the publisher exception hook wrapper to support embedded
# forms in Plone 2.5?
PLONE_25_PUBLISHER_MONKEYPATCH = False
