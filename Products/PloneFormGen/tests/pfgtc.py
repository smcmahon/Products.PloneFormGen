
import email

# Import the base test case classes
from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase.layer import onsetup
import Products.PloneFormGen
try:
    import collective.recaptcha
    haveRecaptcha = True
except ImportError:
    haveRecaptcha = False
    print "collective.recaptcha is unavailable: captcha tests will be skipped."    

from Products.Five.testbrowser import Browser

ZopeTestCase.installProduct('PloneFormGen')

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', Products.PloneFormGen)
    if haveRecaptcha:
        zcml.load_config('configure.zcml', collective.recaptcha)
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
        self.msgtext = messageText
        self.msg = email.message_from_string(messageText.lstrip())

class PloneFormGenTestCase(PloneTestCase.PloneTestCase):
    def _setup(self):
        # make sure we test in Plone 2.5 with the exception hook monkeypatch applied
        Products.PloneFormGen.config.PLONE_25_PUBLISHER_MONKEYPATCH = True
        
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = Session()

class PloneFormGenFunctionalTestCase(PloneTestCase.FunctionalTestCase):

    def _setup(self):
        PloneTestCase.FunctionalTestCase._setup(self)
        self.app.REQUEST['SESSION'] = Session()
        self.browser = Browser()
        self.app.acl_users.userFolderAddUser('root', 'secret', ['Manager'], [])
        self.browser.addHeader('Authorization', 'Basic root:secret')
        self.portal_url = 'http://nohost/plone'
        
    def afterSetUp(self):
        super(PloneTestCase.FunctionalTestCase, self).afterSetUp()
        self.portal.MailHost = MailHostMock()

    def setStatusCode(self, key, value):
        from ZPublisher import HTTPResponse
        HTTPResponse.status_codes[key.lower()] = value
