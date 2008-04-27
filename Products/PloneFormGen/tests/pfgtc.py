
# Import the base test case classes
from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

# Make ZopeTestCase aware of the standard products

# These install (or fail) quietly
#ZopeTestCase.installProduct('CMFCore', quiet=1)
#ZopeTestCase.installProduct('CMFDefault', quiet=1)
#ZopeTestCase.installProduct('CMFCalendar', quiet=1)
#ZopeTestCase.installProduct('CMFTopic', quiet=1)
#ZopeTestCase.installProduct('DCWorkflow', quiet=1)
#ZopeTestCase.installProduct('CMFHelpIcons', quiet=1)
#ZopeTestCase.installProduct('CMFQuickInstallerTool', quiet=1)
#ZopeTestCase.installProduct('CMFFormController', quiet=1)
#ZopeTestCase.installProduct('GroupUserFolder', quiet=1)
#ZopeTestCase.installProduct('ZCTextIndex', quiet=1)
#ZopeTestCase.installProduct('SecureMailHost', quiet=1)
#ZopeTestCase.installProduct('CMFPlone')
#ZopeTestCase.installProduct('Archetypes')
#ZopeTestCase.installProduct('PortalTransforms', quiet=1)
#ZopeTestCase.installProduct('MimetypesRegistry', quiet=1)
#ZopeTestCase.installProduct('kupu', quiet=1)

# These must install cleanly
ZopeTestCase.installProduct('PloneFormGen')

# Set up the Plone site used for the test fixture. The PRODUCTS are the products
# to install in the Plone site (as opposed to the products defined above, which
# are all products available to Zope in the test fixture)
PRODUCTS = ['PloneFormGen']
PloneTestCase.setupPloneSite(products=PRODUCTS)


class PloneFormGenTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
