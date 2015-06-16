
import email

# Import the base test case classes
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing.bbb import PTC_FIXTURE, PloneTestCase
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing import z2

import Products.PloneFormGen
import plone.app.layout
try:
    import collective.recaptcha
    haveRecaptcha = True
except ImportError:
    haveRecaptcha = False
    print "collective.recaptcha is unavailable: captcha tests will be skipped."

from Products.Five.testbrowser import Browser
from Products.MailHost.MailHost import MailHost


class Session(dict):
    def set(self, key, value):
        self[key] = value


class MailHostMock(MailHost):
    def _send(self, mfrom, mto, messageText, immediate=False):
        print '<sent mail from %s to %s>' % (mfrom, mto)
        self.msgtext = messageText
        self.msg = email.message_from_string(messageText.lstrip())


class Fixture(PloneSandboxLayer):

    defaultBases = (PTC_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=Products.PloneFormGen)
        self.loadZCML(package=plone.app.layout)
        if haveRecaptcha:
            self.loadZCML(package=collective.recaptcha)
        z2.installProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'Products.PloneFormGen:default')


FIXTURE = Fixture()

PFG_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='Products.PloneFormGen:Integration',
)
PFG_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE),
    name='Products.PloneFormGen:Functional',
)


class PloneFormGenTestCase(PloneTestCase):

    layer = PFG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        Products.PloneFormGen.config.PLONE_25_PUBLISHER_MONKEYPATCH = True
        self.request.set('SESSION', Session())
        super(PloneFormGenTestCase, self).setUp()
        if getattr(self, 'folder', None) is None:
            setRoles(self.portal, TEST_USER_ID, ['Manager'])
            self.portal.invokeFactory('Folder', 'test-folder')
            setRoles(self.portal, TEST_USER_ID, ['Member'])
            self.folder = self.portal['test-folder']
