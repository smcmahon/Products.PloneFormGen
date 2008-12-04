
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

class Session(dict):
    def set(self, key, value):
        self[key] = value

from Products.SecureMailHost.SecureMailHost import SecureMailHost
class MailHostMock(SecureMailHost):
    def _send(self, mfrom, mto, messageText):
        print '<sent mail from %s to %s>' % (mfrom, mto)

class PloneFormGenTestCase(PloneTestCase.PloneTestCase):
    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = Session()

class PloneFormGenFunctionalTestCase(PloneTestCase.FunctionalTestCase):

    def _setup(self):
        PloneTestCase.FunctionalTestCase._setup(self)
        self.app.REQUEST['SESSION'] = Session()
        
    def afterSetUp(self):
        super(PloneTestCase.FunctionalTestCase, self).afterSetUp()
        self.portal.MailHost = MailHostMock()
