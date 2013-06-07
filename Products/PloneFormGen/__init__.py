""" PloneFormGen, basic Zope Product Initialization """

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

import sys
import logging
logger = logging.getLogger("PloneFormGen")


# let's fail immediately and decisively if our dependencies
# aren't installed
try:
    from Products import PythonField, TALESField, TemplateFields
except ImportError:
    logger.error("PloneFormGen requires the ScriptableFields bundle. See PloneFormGen's README.txt.")
    raise

# Check for Plone versions
try:
    from plone.app.upgrade import v41
    v41  # pyflakes
except ImportError:
    logger.error("PloneFormGen requires Plone >= 4.1.")
    raise

try:
    from plone.app.upgrade import v43
    HAVE_43 = True
except ImportError:
    HAVE_43 = False


from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from AccessControl import ModuleSecurityInfo

from Products.PloneFormGen.config import PROJECTNAME, \
    ADD_CONTENT_PERMISSION, CSA_ADD_CONTENT_PERMISSION, \
    MA_ADD_CONTENT_PERMISSION, SDA_ADD_CONTENT_PERMISSION, \
    SKINS_DIR, GLOBALS

registerDirectory(SKINS_DIR + '/PloneFormGen', GLOBALS)

def initialize(context):

    import content, validators, tools, widgets

    # side-effect import
    import patches

    # Add our tools
    utils.ToolInit('PloneFormGen Tool',
        tools=( tools.formGenTool.FormGenTool, ),
        icon='Form.gif',
        ).initialize(context)


    ##########
    # Add our content types
    # A little different from the average Archetype product
    # due to the need to individualize some add permissions.
    #
    # This approach borrowed from ATContentTypes
    #
    listOfTypes = listTypes(PROJECTNAME)

    content_types, constructors, ftis = process_types(
        listOfTypes,
        PROJECTNAME)
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        if atype.portal_type == 'FormCustomScriptAdapter':
            permission = CSA_ADD_CONTENT_PERMISSION
        elif atype.portal_type == 'FormMailerAdapter':
            permission = MA_ADD_CONTENT_PERMISSION
        elif atype.portal_type == 'FormSaveDataAdapter':
            permission = SDA_ADD_CONTENT_PERMISSION
        else:
            permission = ADD_CONTENT_PERMISSION
        utils.ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permission,
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)


    ModuleSecurityInfo('Products.PloneFormGen').declarePublic('PloneFormGenMessageFactory')


# Import "PloneFormGenMessageFactory as _" to create message ids
# in the ploneformgen domain
from zope.i18nmessageid import MessageFactory
PloneFormGenMessageFactory = MessageFactory('ploneformgen')


# alias for legacy instances of PFGCaptchaField from when it was
# a separate product
try:
    import Products.PFGCaptchaField
except ImportError:
    import Products.PloneFormGen.content.fields
    import Products.PloneFormGen.validators.CaptchaValidator
    Products.PFGCaptchaField = sys.modules['Products.PFGCaptchaField'] = sys.modules['Products.PloneFormGen']
    Products.PFGCaptchaField.field = sys.modules['Products.PFGCaptchaField.field'] = sys.modules['Products.PloneFormGen.content.fields']
    Products.PFGCaptchaField.widget = sys.modules['Products.PFGCaptchaField.widget'] = sys.modules['Products.PloneFormGen.widgets.captcha']
    Products.PFGCaptchaField.validator = sys.modules['Products.PFGCaptchaField.validator'] = sys.modules['Products.PloneFormGen.validators.CaptchaValidator']
else:
    raise "Product Conflict: The functionality of PFGCaptchaField is now included within PloneFormGen.  You must remove the PFGCaptchaField product from your filesystem.  Once you do that, Zope will start and existing captcha fields will continue to work."
