from zope.component import queryMultiAdapter
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable

from Products.PloneFormGen.config import PROPERTY_SHEET_NAME, \
    DEFAULT_MAILTEMPLATE_BODY, EXTRA_ALLOWED

from Products.PloneFormGen.interfaces.field import IPloneFormGenField
from Products.PloneFormGen.interfaces.actionAdapter import \
  IPloneFormGenActionAdapter
from Products.PloneFormGen.interfaces.fieldset import \
  IPloneFormGenFieldset
from Products.PloneFormGen.interfaces.thanksPage import \
  IPloneFormGenThanksPage

class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        return [u'Products.PloneFormGen:loadtest',]

def update_kupu_resources(out, site):
    """ At the time of this writing, kupu's GS export/import
        handling is impractical.  We manage our interactions
        via kupu's arcane api's in the following.
    """
    # Add FormFolder to kupu's linkable types

    kupuTool = getToolByName(site, 'kupu_library_tool', None)
    # skip if no kupuTools
    if kupuTool is None or getattr(kupuTool, 'getPortalTypesForResourceType', None) is None:
        return

    typesTool = getToolByName(site, 'portal_types')
    if kupuTool is not None:
        linkable = list(kupuTool.getPortalTypesForResourceType('linkable'))

        if 'FormFolder' not in linkable:
            # kupu's resource list can accumulate old, no longer valid types;
            # it will throw an exception if we try to resave them.
            # So, let's clean the list.
            valid_types = dict([ (t.id, 1) for t in typesTool.listTypeInfo()])
            linkable = [pt for pt in linkable if pt in valid_types]

            linkable.append('FormFolder')
            kupuTool.updateResourceTypes(({'resource_type' : 'linkable',
                                           'old_type'      : 'linkable',
                                           'portal_types'  :  linkable},))

def safe_add_purgeable_properties(out, site):
    """ In order to avoid a possible "feature" regression and
        to keep test case testModificationsToPropSheetNotOverwritten in
        a passing state, we need to do a check before property add
        of all non-lines properties. This per my reading of GS' PropertiesXMLAdapter's
        _initProperties implementation, which appears to only merge properties of
        type tuple or list.
    """
    ppTool = getToolByName(site, 'portal_properties')
    propSheet = getattr(ppTool, PROPERTY_SHEET_NAME)
    if not propSheet.hasProperty('mail_template'):
        propSheet.manage_addProperty('mail_template', DEFAULT_MAILTEMPLATE_BODY, 'text')
    if not propSheet.hasProperty('mail_body_type'):
        propSheet.manage_addProperty('mail_body_type', 'html', 'string')
    if not propSheet.hasProperty('mail_recipient_email'):
        propSheet.manage_addProperty('mail_recipient_email', '', 'string')
    if not propSheet.hasProperty('mail_recipient_name'):
        propSheet.manage_addProperty('mail_recipient_name', '', 'string')
    if not propSheet.hasProperty('csv_delimiter'):
        propSheet.manage_addProperty('csv_delimiter', ',', 'string')


def importVarious(context):
    """
    Final PloneFormGen import steps.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('ploneformgen-various.txt') is None:
        return
    out = []
    site = context.getSite()
    update_kupu_resources(out, site)
    safe_add_purgeable_properties(out, site)

    ##############
    # set allowed types for insertion in form folder, fieldsets

    # get a list of installed meta types
    ptt = getToolByName(site, 'portal_types')
    att = getToolByName(site, 'archetype_tool')
    metatypes = [ct.content_meta_type for ct in ptt.listTypeInfo()]
    installed_types = [ttype for ttype in att.listTypes() if ttype.meta_type in metatypes]

    # look for PFG fields, fieldsets, thankers and adapters by interface
    fields = [ttype.meta_type for ttype in installed_types
              if IPloneFormGenField.implementedBy(ttype)]
    adapters = [ttype.meta_type for ttype in installed_types
                if IPloneFormGenActionAdapter.implementedBy(ttype)]
    fieldsets = [ttype.meta_type for ttype in installed_types
                 if IPloneFormGenFieldset.implementedBy(ttype)]
    thankers = [ttype.meta_type for ttype in installed_types
                if IPloneFormGenThanksPage.implementedBy(ttype)]

    # can't do captcha field without captcha support, so
    # look for a view named captcha.
    # if there isn't one, remove the field
    if ('FormCaptchaField' in fields) and \
       not queryMultiAdapter((site, site.REQUEST), name='captcha'):
        fields.remove('FormCaptchaField')

    # now, use our hard-won type lists to set allowed types
    ptt.getTypeInfo('FormFolder').manage_changeProperties(
      allowed_content_types = fields + adapters + fieldsets + thankers + \
        EXTRA_ALLOWED
      )
    for fs in fieldsets:
        ptt.getTypeInfo(fs).manage_changeProperties(
          allowed_content_types = fields
          )
