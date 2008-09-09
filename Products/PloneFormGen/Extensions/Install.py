from Products.PloneFormGen import HAS_PLONE30
from Products.PloneFormGen.config import *

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal

from Products.CMFPlone.utils import safe_hasattr

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

from StringIO import StringIO


allTypes = ('FormFolder',) + fieldTypes + adapterTypes + thanksTypes + fieldsetTypes

# Configlets to be added to control panels or removed from them
configlets = (
        { 'id'         : 'PloneFormGen'
        , 'name'       : 'PloneFormGen'
        , 'action'     : 'string:${portal_url}/prefs_pfg_permits'
        , 'condition'  : ''
        , 'category'   : 'Products'
        , 'visible'    : 1
        , 'appId'      : PROJECTNAME
        , 'permission' : ManagePortal
        , 'imageUrl'   : 'Form.gif'
        },
    )


def install(self):
    out = StringIO()

    print >> out, "Installing PloneFormGen"
    # PFG was using this generic setup profile due to an Archetypes 1.5b5
    # bug that was fixed in 1.5rc3.
    # if HAS_PLONE30:
    #     # Archetypes 1.5.0b5 (included with Plone 3.0b3) has a bug which prevents
    #     # installTypes from working unless class name == portal_type.
    #     # Work around it by using portal_setup to handle this part of the install.
    #     #
    #     setup_tool = getToolByName(self, 'portal_setup')
    #     old_context = setup_tool.getImportContextID()
    #     setup_tool.setImportContext('profile-Products.PloneFormGen:typesonly')
    #     setup_tool.runAllImportSteps()
    #     setup_tool.setImportContext(old_context)
    #     print >> out, "Installed types and added to portal_factory via portal_setup"
    # else:
	# Install types
    classes = listTypes(PROJECTNAME)
    installTypes(self, out,
                classes,
                PROJECTNAME)
    
    # for reinstalls: avoid clobbering contained types set up by 3rd-party products
    if hasattr(self.aq_explicit, '_v_pfg_old_allowed_types'):
        pt = getToolByName(self, 'portal_types')
        new_allowed_types = list(pt['FormFolder'].allowed_content_types)
        for t in self._v_pfg_old_allowed_types:
            if t not in new_allowed_types:
                new_allowed_types.append(t)
        pt['FormFolder'].allowed_content_types = new_allowed_types
        delattr(self, '_v_pfg_old_allowed_types')
    print >> out, "Installed types"
    
        # Enable portal_factory
    factory = getToolByName(self, 'portal_factory')
    types = factory.getFactoryTypes().keys()
    for f in allTypes:
        if f not in types:
            types.append(f)
    factory.manage_setPortalFactoryTypes(listOfTypeIds = types)
    print >> out, "Added all my types to portal_factory"

    if HAS_PLONE30:
        # hide properties/references tabs
        pt = getToolByName(self, 'portal_types')
        for typ in types:
            try:
                for act in pt[typ].listActions():
                    if act.id in ['metadata', 'references']:
                        act.visible = False
            except KeyError:
                # prevent breaking on edge case: portal_factories still lists a type that
                # is no longer present in portal_types
                pass

    ## Install skin
    install_subskin(self, out, GLOBALS)
    print >> out, "Installed skin"

    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')
    navtreeProperties = getattr(propsTool, 'navtree_properties')

    # Add the field, fieldset, thanks and adapter types to types_not_searched
    typesNotSearched = list(siteProperties.getProperty('types_not_searched'))
    for f in fieldTypes + adapterTypes + thanksTypes + fieldsetTypes:
        if f not in typesNotSearched:
            typesNotSearched.append(f)
    siteProperties.manage_changeProperties(types_not_searched = typesNotSearched)
    print >> out, "Added form fields & adapters to types_not_searched"

    # Add the field, fieldset, thanks and adapter types to types excluded from navigation
    typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
    for f in fieldTypes + adapterTypes + thanksTypes + fieldsetTypes:
        if f not in typesNotListed:
            typesNotListed.append(f)
    navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)
    print >> out, "Added form fields & adapters to metaTypesNotToList"

    # Set up the workflow for the field, fieldset, thanks and adapter types: there should be none!
    wft = getToolByName(self, 'portal_workflow')
    wft.setChainForPortalTypes(fieldTypes + adapterTypes + thanksTypes + fieldsetTypes, ())
    print >> out, "Set up empty field and adapter workflows."

    # Add to default_page_types
    defaultPageTypes = list(siteProperties.getProperty('default_page_types'))
    if 'FormFolder' not in defaultPageTypes:
        defaultPageTypes.append('FormFolder')
    siteProperties.manage_changeProperties(default_page_types = defaultPageTypes)
    print >> out, "Added FormFolder to default_page_types"

    # Add FormFolder to kupu's linkable types
    kupuTool = getToolByName(self, 'kupu_library_tool', None)
    if kupuTool is not None:
        linkable = list(kupuTool.getPortalTypesForResourceType('linkable'))
        if 'FormFolder' not in linkable:
            linkable.append('FormFolder')
        # See optilude's note in the RichDocument install re why this is so odd.
        kupuTool.updateResourceTypes(({'resource_type' : 'linkable',
                                       'old_type'      : 'linkable',
                                       'portal_types'  :  linkable},))
        print >> out, "Added FormFolder to kupu's linkable types"

    if not safe_hasattr(self, 'formgen_tool'):
        portalObject = getToolByName(self, 'portal_url').getPortalObject()
        addTool = portalObject.manage_addProduct['PloneFormGen'].manage_addTool
        addTool('PloneFormGen Tool')
    print >> out, "Added PloneFormGen Tool"

    
    # add property sheet in portal_properties
    # we'll use this to store site defaults
    ppTool = getToolByName(self, 'portal_properties')
    if not safe_hasattr(ppTool, PROPERTY_SHEET_NAME):
        ppTool.addPropertySheet(PROPERTY_SHEET_NAME, 'PloneFormGen properties')
        print >> out, "Added PloneFormGen properysheet"
    else:
        print >> out, "Using existing propertysheet"
    propSheet = getattr(ppTool, PROPERTY_SHEET_NAME)
    if not propSheet.hasProperty('permissions_used'):
        propSheet.manage_addProperty('permissions_used', pfgPermitList, 'lines')
    if not propSheet.hasProperty('mail_template'):
        propSheet.manage_addProperty('mail_template', DEFAULT_MAILTEMPLATE_BODY, 'text')    
    if not propSheet.hasProperty('mail_body_type'):
        propSheet.manage_addProperty('mail_body_type', 'html', 'string')    
    if not propSheet.hasProperty('mail_recipient_email'):
        propSheet.manage_addProperty('mail_recipient_email', '', 'string')    
    if not propSheet.hasProperty('mail_recipient_name'):
        propSheet.manage_addProperty('mail_recipient_name', '', 'string')
    if not propSheet.hasProperty('mail_cc_recipients'):
        propSheet.manage_addProperty('mail_cc_recipients', [], 'lines')
    if not propSheet.hasProperty('mail_bcc_recipients'):
        propSheet.manage_addProperty('mail_bcc_recipients', [], 'lines')
    if not propSheet.hasProperty('mail_xinfo_headers'):
        propSheet.manage_addProperty('mail_xinfo_headers', XINFO_DEFAULT, 'lines')
    if not propSheet.hasProperty('mail_add_headers'):
        propSheet.manage_addProperty('mail_add_headers', [], 'lines')
    

    # add the configlets to the portal control panel
    configTool = getToolByName(self, 'portal_controlpanel', None)
    productConfiglets = [co['id'] for co in configTool.enumConfiglets(group='Products')]
    if 'PloneFormGen' not in productConfiglets:
        for conf in configlets:
            try:
                configTool.registerConfiglet(**conf)
                out.write('Added configlet %s\n' % conf['id'])
            except:
                out.write('Configlet already configured\n')
    else:
        out.write('Unexpectedly found an existing configlet for PFG. Skipped configlet registration.')        


    if HAS_PLONE30:
        # register kss resource
        kssRegTool = getToolByName(self, 'portal_kss', None)
        # if our kss item is already in the registry, let's
        # yank it out so that we force the registry to update
        try:
            kssRegTool.manage_removeKineticStylesheet('ploneformgen.kss')
        except:
            pass
        kssRegTool.registerKineticStylesheet('ploneformgen.kss')
        out.write('Added ploneformgen.kss to kss registry\n')


    ##
    ## Print install info
    ##
    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()


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


def addSkinLayer(self, layer):
    """ Add a layer immediately after custom to all skinpaths """
    
    skinstool = getToolByName(self, 'portal_skins')
    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName)
        path = [i.strip() for i in  path.split(',')]
        try:
            if layer not in path:
                path.insert(path.index('custom') +1, layer)
        except ValueError:
            if layer not in path:
                path.append(layer)
        path = ','.join(path)
        skinstool.addSkinSelection(skinName, path)


def uninstall_tool(self, out):
    try:
        self.manage_delObjects(['formgen_tool'])
    except:
        pass
    else:
        print >>out, "PloneFormGen tool removed"


def uninstall_configlet(self, out):
    # remove the configlets from the portal control panel
    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            configTool.unregisterConfiglet(conf['id'])
            out.write('Removed configlet %s\n' % conf['id'])

def beforeUninstall(self, reinstall, product, cascade):
    # for reinstalls: store list of allowed contained types,
    # so we don't lose anything that a 3rd-party product added.
    # This is ugly, but I'm not sure where else to stash this,
    # since this is an external method and I can't seem to use
    # a global variable.
    pt = getToolByName(self, 'portal_types')
    try:
        self._v_pfg_old_allowed_types = pt['FormFolder'].allowed_content_types
    except KeyError:
        self._v_pfg_old_allowed_types = None

    return '', cascade

def uninstall(self):
    out = StringIO()

    uninstall_tool(self, out)
    
    uninstall_configlet(self, out)
    

    # remove FormFolder from kupu's linkable types
    kupuTool = getToolByName(self, 'kupu_library_tool')
    linkable = list(kupuTool.getPortalTypesForResourceType('linkable'))
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
    removeSkinLayer(self, 'PloneFormGenPlone3')
    # skinstool = getToolByName(self, 'portal_skins')
    # for skinName in skinstool.getSkinSelections():
    #     path = skinstool.getSkinPath(skinName)
    #     path = [i.strip() for i in  path.split(',')]
    #     for alayer in ('PloneFormGen', 'PloneFormGenPlone3',):
    #         if alayer in path:
    #             path.remove(alayer)
    #     path = ','.join(path)
    #     skinstool.addSkinSelection(skinName, path)
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
