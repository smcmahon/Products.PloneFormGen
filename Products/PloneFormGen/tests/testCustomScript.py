"""

    Unit test for PloneFormGen custom scripts

    Copyright 2006 Red Innovation http://www.redinnovation.com

"""
__author__  = 'Mikko Ohtamaa <mikko@redinnovation.com>'
__docformat__ = 'plaintext'

try:
    from App.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass

from AccessControl import Unauthorized
from AccessControl import ClassSecurityInfo
from Products.PythonScripts.PythonScript import PythonScript, manage_addPythonScript

from zExceptions import Forbidden

from Products.PloneFormGen.tests import pfgtc

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

test_script="""
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen, request
##title=Succesfully working script
##

from Products.CMFCore.utils import getToolByName

assert fields["test_field"] == "123"
return "foo"
"""

bad_parameters_script="""
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=
##title=
##

return 'foo'
"""

syntax_error_script="""
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen, request
##title=
##
if:
return asdfaf
"""

runtime_error_script="""
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen
##title=
##
return "asdfaf" + 1
"""

security_script="""
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen, request
##title=Script needing special privileges
##

from Products.CMFCore.utils import getToolByName

portal_url = getToolByName(context, "portal_url")
portal = portal_url.getPortalObject()

# Try set left_slots
portal.manage_addProperty('foo', ['foo'], 'lines')
"""

proxied_script="""
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen, request
##title=Script needing special privileges
##

# Should raise Unauthorized
return request.fooProtected()
"""

default_params_script = \
"""
fields
ploneformgen
request
"""

class FakeRequest(dict):

    def __init__(self, **kwargs):
        self.form = kwargs

class SecureFakeRequest(dict):

    security = ClassSecurityInfo()

    def __init__(self, **kwargs):
        self.form = kwargs

    security.declareProtected(permissions.ManagePortal,
                              'fooProtected')
    def fooProtected(self):
        """ Only manager can access this """
        return "foo"

InitializeClass(SecureFakeRequest)


class TestCustomScript(pfgtc.PloneFormGenTestCase):
    """ Test FormCustomScriptAdapter functionality in PloneFormGen """

    def setUp(self):
        pfgtc.PloneFormGenTestCase.setUp(self)

        self.loginAsPortalOwner()

        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        self.ff1.invokeFactory('FormStringField', 'test_field')


    def createScript(self):
        """ Creates FormCustomScript object """
        # 1. Create custom script adapter in the form folder
        self.ff1.invokeFactory('FormCustomScriptAdapter', 'adapter')

        # 2. Check that creation succeeded
        self.failUnless('adapter' in self.ff1.objectIds())
        adapter = self.ff1.adapter

        # 3. Set action adapter
        self.ff1.setActionAdapter( ('adapter',) )
        self.assertEqual(self.ff1.actionAdapter, ('adapter',))

#    def testScriptTypes(self):
#        """ Check DisplayList doesn't fire exceptions """
#        self.createScript()
#        adapter = self.ff1.adapter
#        adapter.getScriptTypeChoices()

    def testSuccess(self):
        """ Succesful script execution

        Creates a script, some form content,
        executes form handling.
        """

        self.createScript()

        adapter = self.ff1.adapter
        # 4. Set script data
        adapter.setScriptBody(test_script)

        req = FakeRequest(test_field="123")

        errors = adapter.validate()
        assert len(errors) == 0, "Had errors:" + str(errors)

        # Execute script
        # XXX TODO: we don't want to rely on return value from onSuccess
        reply = adapter.onSuccess(self.ff1, req)
        assert reply == "foo", "Script returned:" + str(reply)

    def testRunTimeError(self):
        """ Script has run-time error """
        self.createScript()

        adapter = self.ff1.adapter
        # 4. Set script data
        adapter.setScriptBody(runtime_error_script)

        errors = adapter.validate()
        assert len(errors) == 0, "Had errors:" + str(errors)

        # Execute script
        throwed = False
        try:
            reply = adapter.onSuccess([])
        except TypeError, e:
            reply = None
            throwed = True

        assert throwed, "Bad script didn't throw run-time exception, got " + str(reply)
        assert reply == None

    def testSyntaxError(self):
        """ Script has syntax errors

        TODO: Syntax errors are not returned in validation?
        """

        # Note: this test logs an error message; it does not indicate test failure

        self.createScript()

        adapter = self.ff1.adapter
        # 4. Set script data
        adapter.setScriptBody(syntax_error_script)

        # Execute script
        throwed = False
        try:
            adapter.onSuccess([])
        except ValueError, e:
            throwed = True

        assert throwed, "Bad script didn't throw run-time exception"


    def testBadParameters(self):
        """ Invalid number of script parameters """

        self.createScript()

        adapter = self.ff1.adapter
        # 4. Set script data
        adapter.setScriptBody(bad_parameters_script)

        errors = adapter.validate()
        assert len(errors) == 0, "Had errors:" + str(errors)

        # Execute script
        throwed = False
        try:
            adapter.onSuccess([])
        except TypeError:
            throwed=True
        assert throwed, "Invalid parameters failed silently"


    def testDefaultParameters(self):
        """ Test to make sure the documented parameters are available """

        self.createScript()

        adapter = self.ff1.adapter
        adapter.setScriptBody(default_params_script)

        request = FakeRequest(topic = 'test subject', replyto='test@test.org', comments='test comments')

        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )


#    def testSecurity(self):
#        """ Script needing proxy role
#
#        TODO: Why no security exceptions are raised?
#        """
#        #self.createScript()
#
#        #adapter = self.ff1.adapter
#        # 4. Set script data
#        #adapter.setScriptBody(security_script)
#
#        #errors = adapter.validate()
#        #assert len(errors) == 0, "Had errors:" + str(errors)
#
#        # Execute script
#        #throwed = False
#
#        #adapter.onSuccess([])
#
#        #if hasattr(self.portal, "foo"):
#        #    assert "Script executed under full priviledges"
#
#        #self.failUnless(throwed==True, "Bypassed security, baaad!")
#
#        pass


    def testSetProxyRole(self):
        """ Exercise setProxyRole """

        self.createScript()
        adapter = self.ff1.adapter

        adapter.setProxyRole('Manager')
        adapter.setProxyRole('none')

        self.assertRaises(Forbidden, adapter.setProxyRole, 'bogus')


# XXX TODO: We need to find another way to test this.
#    def testProxyRole(self):
#        """ Test seeing how setting proxy role affects unauthorized exception """
#
#        # TODO: Zope security system kills me
#
#        #self.createScript()
#
#        #adapter = self.ff1.adapter
#        # 4. Set script data
#        #adapter.setScriptBody(proxied_script)
#
#        #req = SecureFakeRequest(test_field="123")
#        #req = req.__of__(self.portal)
#
#        #errors = adapter.validate()
#        #assert len(errors) == 0, "Had errors:" + str(errors)
#
#        # Execute script
#        #throwed = False
#        #try:
#        #    adapter.onSuccess([], req)
#        #except Unauthorized:
#        #    throwed=True
#
#        #assert throwed, "No Unauthorized was raised"
#
#        #self.loginAsPortalOwner()
#        #self.setRoles(["Manager", "Owner"])
#        #adapter.setProxyRole("Manager")
#        #self.logout()
#
#        assert adapter.onSuccess([], req) == "123"

#    def testSkinsScript(self):
#        """ Test executing script from portal_skins """
#        portal_skins = self.portal.portal_skins
#        manage_addPythonScript(portal_skins.custom, "test_skins_script")
#        test_skins_script = portal_skins.custom.test_skins_script
#
#        test_skins_script.ZPythonScript_edit("", test_script)
#        self._refreshSkinData()
#
#
#        portal_skins.custom.test_skins_script({"test_field" : "123"}, "foo", None)
#        # Do a dummy test call
#        self.portal.test_skins_script({"test_field" : "123"}, "foo", None)
#
#        self.createScript()
#        adapter = self.ff1.adapter
#        adapter.setScriptType("skins_script")
#        adapter.setScriptName("test_skins_script")
#
#        errors = adapter.validate()
#        assert len(errors) == 0, "Had errors:" + str(errors)
#
#        # Execute script
#        req = FakeRequest(test_field="123")
#        reply = adapter.onSuccess([], req)
#        assert reply == "foo", "Script returned:" + str(reply)
