"""DataGridFF install routine"""

__author__  = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'


from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.utils import safe_hasattr

from Products.CMFFormController.FormAction import FormActionKey

from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.Extensions.utils import install_subskin
from Products.Archetypes.public import listTypes

from StringIO import StringIO

from Products.PFGDataGrid.config import *

def install(self):
    """Install PFGDataGrid"""

    
    #######################
    # Both PloneFormGen and the target field provider are going to have to be installed
    # first. So, let's check.
    
    portal_skins = getToolByName(self, 'portal_skins')
    assert safe_hasattr(portal_skins, 'DataGridWidget'), "DataGridField must be installed prior to installing this product."
    assert safe_hasattr(portal_skins, 'PloneFormGen'), "PloneFormGen must be installed prior to installing this product."

    # Safe to proceed.

    classes = listTypes(PROJECTNAME)
    
    # get a list of types provided by this product
    # note that this trick will cause problems if the meta_type doesn't match class name
    myTypes = [item['name'] for item in classes]

    out = StringIO()

    print >> out, "Installing %s" % PROJECTNAME


    # boilerplate setup of DynamicViewFTI and factory

    installTypes(self, out,
                 classes,
                 PROJECTNAME)
    print >> out, "Installed types"

    factory = getToolByName(self, 'portal_factory')
    types = factory.getFactoryTypes().keys()
    for add_type in myTypes:
        if add_type not in types:
            types.append(add_type)
            factory.manage_setPortalFactoryTypes(listOfTypeIds = types)

    print >> out, "Added %s to portal_factory" % ', '.join(myTypes)


    #######################
    # form fields should not be visible to navigation or search.
    # they should have no workflow of their own.
    
    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')
    navtreeProperties = getattr(propsTool, 'navtree_properties')

    # Add to types_not_searched
    typesNotSearched = list(siteProperties.getProperty('types_not_searched'))
    for f in myTypes:
        if f not in typesNotSearched:
            typesNotSearched.append(f)
    siteProperties.manage_changeProperties(types_not_searched = typesNotSearched)
    print >> out, "Added %ss to types_not_searched" % ', '.join(myTypes)

    # Add to types excluded from navigation
    typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
    for f in myTypes:
        if f not in typesNotListed:
            typesNotListed.append(f)
    navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)
    print >> out, "Added %s to metaTypesNotToList" % ', '.join(myTypes)

    # Set up the workflow: there should be none!
    wft = getToolByName(self, 'portal_workflow')
    wft.setChainForPortalTypes(myTypes, ())
    print >> out, "Set up empty workflows for %s." % ', '.join(myTypes)


    #######################
    # Here's the code specific to making this visible to PloneFormGen

    portal_types = getToolByName(self, 'portal_types')
    for typeName in ('FormFolder', 'FieldsetFolder'):
        ptType = portal_types.getTypeInfo(typeName)
        ffact = list(ptType.allowed_content_types)
        ffact += myTypes
        ptType.manage_changeProperties(allowed_content_types = ffact)
    print >> out, "Added %s to allowed_content_types for %s" % (', '.join(myTypes), typeName)

    # End PFG installation
    #######################
    


    print >> out, "Done."
    return out.getvalue()



