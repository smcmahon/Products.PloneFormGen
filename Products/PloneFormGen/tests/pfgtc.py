
# Import the base test case classes
from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase.layer import onsetup
import Products.PloneFormGen

ZopeTestCase.installProduct('PloneFormGen')

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', Products.PloneFormGen)
    fiveconfigure.debug_mode = False

# Set up the Plone site used for the test fixture. The PRODUCTS are the products
# to install in the Plone site (as opposed to the products defined above, which
# are all products available to Zope in the test fixture)
setup_product()
PloneTestCase.setupPloneSite(products=['PloneFormGen'])



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
