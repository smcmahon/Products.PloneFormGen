""" PloneFormGen, basic Zope Product Initialization """

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger("PloneFormGen")


# let's fail immediately and decisively if our dependencies
# aren't installed
try:
    from Products import PythonField, TALESField, TemplateFields
except ImportError:
    logger.error("PloneFormGen requires the ScriptableFields bundle. See PloneFormGen's README.txt.")
    raise

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
    ModuleSecurityInfo('Products.PloneFormGen').declarePublic('HAS_PLONE25')


# Import "PloneFormGenMessageFactory as _" to create message ids
# in the ploneformgen domain
# Zope 3.1-style messagefactory module
# BBB: Zope 2.8 / Zope X3.0
try:
    from zope.i18nmessageid import MessageFactory
except ImportError:
    from messagefactory_ import PloneFormGenMessageFactory
else:
    PloneFormGenMessageFactory = MessageFactory('ploneformgen')

# Check for Plone versions
try:
    from Products.CMFPlone.migrations import v2_5
except ImportError:
    HAS_PLONE25 = False
else:
    HAS_PLONE25 = True
try:
    from Products.CMFPlone.migrations import v3_0
except ImportError:
    HAS_PLONE30 = False
else:
    HAS_PLONE30 = True

