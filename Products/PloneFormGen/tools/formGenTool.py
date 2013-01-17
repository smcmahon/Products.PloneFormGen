""" FormGenTool manages site-wide PloneFormGen settings """

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

from types import StringTypes

from AccessControl import ClassSecurityInfo
from AccessControl.PermissionRole import rolesForPermissionOn
from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.permissions import View, ManagePortal, ModifyPortalContent
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFPlone.utils import safe_hasattr

from Products.Archetypes.utils import DisplayList

from Products.validation import validation
from Products.validation.validators.RegexValidator import RegexValidator

try:
    from App.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass

from Products.PloneFormGen import config

from Products.PloneFormGen import PloneFormGenMessageFactory as _


class FormGenTool(UniqueObject, SimpleItem):
    """ FormGenTool manages site-wide PloneFormGen settings """

    id = 'formgen_tool'
    meta_type= 'PloneFormGen Tool'
    title = 'PloneFormGen Settings'
    plone_tool = True
    security = ClassSecurityInfo()


    def __init__(self):
        self._initStringValidators()


    security.declarePrivate('_initStringValidators')
    def _initStringValidators(self):
        """ Initialize string validators from config
        """

        self.stringValidators = {}
        self.stringValidatorsDL = DisplayList()
        self.stringValidatorsDL.add('vocabulary_none_text', u'None')

        for kwa in config.stringValidators:
            id = kwa['id']

            title = kwa.get('title', id)
            i18nid = kwa.get('i18nid', title)

            errmsg = kwa.get('errmsg', 'Validation failed: %s' % id)
            errid = kwa.get('errid', errmsg)
            errmsg = _(errid, errmsg)

            validatorId = 'pfgv_%s' % id
            self.stringValidators[id] = {
                'title'  : title,
                'i18nid' : i18nid,
                'errmsg' : errmsg,
                'errid'  : errid,
                # 'revalid': revalid,
                'id'     : validatorId,
                }

            self.stringValidatorsDL.add( id, title, msgid=i18nid )


    def getStringValidatorsDL(self):
        """ return a display list of string validators
        """

        if not getattr(self, 'stringValidators', False):
            # on-demand migration from PFG < 1.2
            self._initStringValidators()

        # self._initStringValidators()

        return self.stringValidatorsDL


    security.declarePrivate('getFromPropSheet')
    def getFromPropSheet(self, propid, default):
        """ find a property value in the property sheet
            with a fallback """

        res = default
        ppTool = getToolByName(self, 'portal_properties')
        psheet = getattr(ppTool, config.PROPERTY_SHEET_NAME, None)
        if psheet is not None:
            res = psheet.getProperty(propid, res)
        return res


    security.declareProtected(ManagePortal, 'setDefault')
    def setDefault(self, propid, default):
        """ change a property in the portal_properties sheet """

        ppTool = getToolByName(self, 'portal_properties')
        psheet = getattr(ppTool, config.PROPERTY_SHEET_NAME)
        psheet.manage_changeProperties( **{propid : default} )


    security.declareProtected(ManagePortal, 'getPfgPermissions')
    def getPfgPermissions(self):
        """ get permissions in use by PFG """

        return self.getFromPropSheet('permissions_used', config.pfgPermitList)


    security.declareProtected(ModifyPortalContent, 'getDefaultMailTemplateBody')
    def getDefaultMailTemplateBody(self):
        """ get the site's default mail adapter mail body template """

        return self.getFromPropSheet('mail_template', config.DEFAULT_MAILTEMPLATE_BODY)


    security.declareProtected(ModifyPortalContent, 'getDefaultMailRecipient')
    def getDefaultMailRecipient(self):
        """ get the site's default mail adapter recipient """

        return self.getFromPropSheet('mail_recipient_email', '')


    security.declareProtected(ModifyPortalContent, 'getDefaultMailCC')
    def getDefaultMailCC(self):
        """ get the site's default mail cc """

        return self.getFromPropSheet('mail_cc_recipients', [])


    security.declareProtected(ModifyPortalContent, 'getDefaultMailBCC')
    def getDefaultMailBCC(self):
        """ get the site's default mail cc """

        return self.getFromPropSheet('mail_bcc_recipients', [])


    security.declareProtected(ModifyPortalContent, 'getDefaultMailRecipientName')
    def getDefaultMailRecipientName(self):
        """ get the site's default mail adapter recipient name """

        return self.getFromPropSheet('mail_recipient_name', '')


    security.declareProtected(ModifyPortalContent, 'getDefaultMailBodyType')
    def getDefaultMailBodyType(self):
        """ get the site's default mail adapter mail body template """

        return self.getFromPropSheet('mail_body_type', 'html')


    security.declareProtected(ModifyPortalContent, 'getCSVDelimiter')
    def getCSVDelimiter(self):
        """ get the site's default csv delimiter for data export """

        return self.getFromPropSheet('csv_delimiter', ',')


    security.declareProtected(ModifyPortalContent, 'getDefaultMailXInfo')
    def getDefaultMailXInfo(self):
        """ get the site's default mail adapter xinfo headers """

        return self.getFromPropSheet('mail_xinfo_headers', config.XINFO_DEFAULT)


    security.declareProtected(ModifyPortalContent, 'getDefaultMailAddHdrs')
    def getDefaultMailAddHdrs(self):
        """ get the site's default mail adapter additional headers """

        return self.getFromPropSheet('mail_add_headers', [])


    security.declareProtected(ManagePortal, 'rolesForPermission')
    def rolesForPermission(self, permit):
        """
         return list of roles for permission,
         ready to use in permissions configlet
        """

        portal=getToolByName(self, 'portal_url').getPortalObject()

        livePermits = rolesForPermissionOn(permit, portal)
        myPermits = list(self.getPfgPermissions())
        index = myPermits.index(permit)
        rpos = 0
        res = []
        for role in portal.rolesOfPermission(permit):
            name = role['name']
            if name not in ['Anonymous', 'Authenticated']:
                id = "p%dr%d" % (index, rpos)
                if name in livePermits:
                    checked = 'CHECKED'
                else:
                    checked = None
                res.append( {'label':name, 'id':id, 'checked':checked,} )
            rpos += 1
        return res


    security.declareProtected(ManagePortal, 'setRolePermits')
    def setRolePermits(self, REQUEST):
        """
        Set role/permissions on portal based on REQUEST.form.
        For use in configlet.
        """

        portal=getToolByName(self, 'portal_url').getPortalObject()
        permits = list(self.getPfgPermissions())

        # build list of roles selected in form
        for index in range(0, len(permits)):
            permit = permits[index]
            # look to see if there is a marker for permit
            # in the form. That makes sure we don't set unintended
            # permissions.
            if REQUEST.form.get(permit, '0') == '1':
                allRoles = portal.rolesOfPermission(permit)
                rpos = 0
                roles = []
                for rpos in range(0, len(allRoles)):
                    id = "p%dr%d" % (index, rpos)
                    if REQUEST.form.get(id, '0') == '1':
                        roles.append(allRoles[rpos]['name'])
                # set role permissions
                portal.manage_permission(permit, roles)


InitializeClass(FormGenTool)

# since we're in a singleton's module anyway,
# this is a convenient place to register the
# custom string validators

def _registerStringValidators():

    for kwa in config.stringValidators:
        id = kwa['id']

        errmsg = kwa.get('errmsg', 'Validation failed: %s' % id)
        errid = kwa.get('errid', errmsg)
        errmsg = _(errid, errmsg)

        # create a validator to match, register it.
        validatorId = 'pfgv_%s' % id
        revalid = RegexValidator(validatorId,
            kwa.get('regex', '.+'),
            ignore=kwa.get('ignore', ''),
            )
        validation.register(revalid)

_registerStringValidators()
