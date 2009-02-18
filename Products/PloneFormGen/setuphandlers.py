from Products.CMFCore.utils import getToolByName
from Products.PloneFormGen.config import PROPERTY_SHEET_NAME, \
    DEFAULT_MAILTEMPLATE_BODY

def update_kupu_resources(out, site):
    """ At the time of this writing, kupu's GS export/import
        handling is impractical.  We manage our interactions
        via kupu's arcane api's in the following.
    """
    # Add FormFolder to kupu's linkable types

    typesTool = getToolByName(site, 'portal_types')
    kupuTool = getToolByName(site, 'kupu_library_tool', None)
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
