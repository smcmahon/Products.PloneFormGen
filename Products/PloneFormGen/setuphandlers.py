from Products.CMFCore.utils import getToolByName

def update_kupu_resources(out, site):
    """ At the time of this writing, kupu's GS export/import
        handling is impractical.  We manage our interactions
        via kupu's arcane api's in the following.
    """
    # Add FormFolder to kupu's linkable types
    kupuTool = getToolByName(site, 'kupu_library_tool', None)
    if kupuTool is not None:
        linkable = list(kupuTool.getPortalTypesForResourceType('linkable'))
        if 'FormFolder' not in linkable:
            linkable.append('FormFolder')
        # See optilude's note in the RichDocument install re why this is so odd.
        kupuTool.updateResourceTypes(({'resource_type' : 'linkable',
                                       'old_type'      : 'linkable',
                                       'portal_types'  :  linkable},))

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
