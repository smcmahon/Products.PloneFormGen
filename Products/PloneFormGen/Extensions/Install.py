from Products.PloneFormGen import HAS_PLONE30
from Products.PloneFormGen.config import *

from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

def install(self):
    """ BBB: Make for a pleasant installation experience in 2.5.x.
        To be removed when eliminating support for < 3.x.
    """
    out = StringIO()
    
    # We install our product by running a GS profile.  We use the old-style Install.py module 
    # so that our product works w/ the Quick Installer in Plone 2.5.x
    print >> out, "Installing PloneFormGen"
    setup_tool = getToolByName(self, 'portal_setup')
    if HAS_PLONE30:
        setup_tool.runAllImportStepsFromProfile(
                "profile-Products.PloneFormGen:default",
                purge_old=False)
    else:
        # BBB: remove conditional once PFG no longer supports 2.5.x
        old_context = setup_tool.getImportContextID()
        
        # run the standard install process
        setup_tool.setImportContext('profile-Products.PloneFormGen:default')
        setup_tool.runAllImportSteps()
        
        # BBB: make 2.5.x specific overrides
        setup_tool.setImportContext('profile-Products.PloneFormGen:typeoverrides25x')
        setup_tool.runAllImportSteps()
        
        setup_tool.setImportContext(old_context)
    


def removeSkinLayer(self, layer):
    """ Remove a skin layer from all skinpaths """

    skinstool = getToolByName(self, 'portal_skins')
    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName)
        path = [i.strip() for i in  path.split(',')]
        if layer in path:
            path.remove(layer)
            path = ','.join(path)
            skinstool.addSkinSelection(skinName, path)

def uninstall_tool(self, out):
    try:
        self.manage_delObjects(['formgen_tool'])
    except:
        pass
    else:
        print >>out, "PloneFormGen tool removed"


def uninstall(self):
    out = StringIO()

    uninstall_tool(self, out)
    
    # remove FormFolder from kupu's linkable types
    kupuTool = getToolByName(self, 'kupu_library_tool', None)
    typesTool = getToolByName(self, 'portal_types')
    if kupuTool is not None:
        linkable = list(kupuTool.getPortalTypesForResourceType('linkable'))

        # prune linkable to really existing types
        valid_types = dict([ (t.id, 1) for t in typesTool.listTypeInfo()])
        linkable = [pt for pt in linkable if pt in valid_types]

        if 'FormFolder' in linkable:
            linkable.remove('FormFolder')
        kupuTool.updateResourceTypes(({'resource_type' : 'linkable',
                                       'old_type'      : 'linkable',
                                       'portal_types'  :  linkable},))
        print >> out, "Removed FormFolder from kupu's linkable types"


    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')
    navtreeProperties = getattr(propsTool, 'navtree_properties')

    # remove the field, thanks and adapter types from types excluded from navigation
    typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
    for f in fieldTypes + adapterTypes + thanksTypes, fieldsetTypes:
        if f in typesNotListed:
            typesNotListed.remove(f)
    navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)
    print >> out, "Removed form fields & adapters from metaTypesNotToList"

    # Remove the field, thanks and adapter types from types_not_searched
    typesNotSearched = list(siteProperties.getProperty('types_not_searched'))
    for f in fieldTypes + adapterTypes + thanksTypes + fieldsetTypes:
        if f in typesNotSearched:
            typesNotSearched.remove(f)
    siteProperties.manage_changeProperties(types_not_searched = typesNotSearched)
    print >> out, "Removed form fields & adapters from types_not_searched"

    # Remove from default_page_types
    defaultPageTypes = list(siteProperties.getProperty('default_page_types'))
    if 'FormFolder' in defaultPageTypes:
        defaultPageTypes.remove('FormFolder')
        siteProperties.manage_changeProperties(default_page_types = defaultPageTypes)
    print >> out, "Removed FormFolder from default_page_types"

    # Remove from use_folder_tabs 
    use_folder_tabs = list(siteProperties.getProperty('use_folder_tabs'))
    if 'FormFolder' in use_folder_tabs:
        use_folder_tabs.remove('FormFolder')
    if 'FieldsetFolder' in use_folder_tabs:
        use_folder_tabs.remove('FieldsetFolder')
    siteProperties.manage_changeProperties(use_folder_tabs = use_folder_tabs)
    print >> out, "Removed FormFolder and FieldsetFolder from use_folder_tabs"

    # Remove from typesLinkToFolderContentsInFC 
    typesLinkToFolderContentsInFC = list(siteProperties.getProperty('typesLinkToFolderContentsInFC'))
    if 'FormFolder' in typesLinkToFolderContentsInFC:
        typesLinkToFolderContentsInFC.remove('FormFolder')
    if 'FieldsetFolder' in typesLinkToFolderContentsInFC:
        typesLinkToFolderContentsInFC.remove('FieldsetFolder')
    siteProperties.manage_changeProperties(typesLinkToFolderContentsInFC = typesLinkToFolderContentsInFC)
    print >> out, "Removed FormFolder and FieldsetFolder from typesLinkToFolderContentsInFC"

    # Remove skin directory from skin selections
    removeSkinLayer(self, 'PloneFormGen')
    print >> out, "Removed PloneFormGen layers from all skin selections"

    if HAS_PLONE30:
        kssRegTool = getToolByName(self, 'portal_kss', None)
        kssRegTool.manage_removeKineticStylesheet('ploneformgen.kss')
        print >> out, "Removed ploneformgen.kss from kss registry"

    print >> out, """\nNOTE: portal_properties/ploneformgen_properties
    was left in place so that you may reinstall without losing site
    configuration data. It's harmless, but feel free to delete it if
    you're sure you don't need any pfg site configuration changes."""

    print >> out, "\nSuccessfully uninstalled %s." % PROJECTNAME
    return out.getvalue()
