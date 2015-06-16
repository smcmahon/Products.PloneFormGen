#
# Test PloneFormGen top-level functionality
#

from Products.PloneFormGen.tests import pfgtc

from Products.CMFCore.utils import getToolByName

class FakeRequest(dict):

    def __init__(self, **kwargs):
        self.form = kwargs


class TestTools(pfgtc.PloneFormGenTestCase):
    """ test our tool """

    def test_FormGenTool(self):
        fgt = getToolByName(self.portal, 'formgen_tool')

        pt = getToolByName(self.portal, 'portal_properties').ploneformgen_properties

        fgt.setDefault('permissions_used', ['test text'])
        fgt.setDefault('mail_template', 'something')
        fgt.setDefault('mail_body_type', 'text')
        fgt.setDefault('mail_recipient_email', 'eggs')
        fgt.setDefault('mail_recipient_name', 'spam')
        fgt.setDefault('mail_cc_recipients', ['spam and eggs'])
        fgt.setDefault('mail_bcc_recipients', ['eggs and spam'])
        fgt.setDefault('mail_xinfo_headers', ['one', 'two'])
        fgt.setDefault('mail_add_headers',['three', 'four'])
        fgt.setDefault('csv_delimiter','|')

        permits = fgt.getPfgPermissions()
        self.failUnlessEqual(len(permits), 1)
        self.failUnlessEqual(permits[0], 'test text')

        self.failUnlessEqual(fgt.getDefaultMailTemplateBody(), 'something')
        self.failUnlessEqual(fgt.getDefaultMailBodyType(), 'text')
        self.failUnlessEqual(fgt.getDefaultMailRecipient(), 'eggs')
        self.failUnlessEqual(fgt.getDefaultMailRecipientName(), 'spam')
        self.failUnlessEqual(fgt.getCSVDelimiter(), '|')

        cc = fgt.getDefaultMailCC()
        self.failUnlessEqual(len(cc), 1)
        self.failUnlessEqual(cc[0], 'spam and eggs')

        bcc = fgt.getDefaultMailBCC()
        self.failUnlessEqual(len(bcc), 1)
        self.failUnlessEqual(bcc[0], 'eggs and spam')

        xi = fgt.getDefaultMailXInfo()
        self.failUnlessEqual(len(xi), 2)
        self.failUnlessEqual(xi[0], 'one')

        xi = fgt.getDefaultMailAddHdrs()
        self.failUnlessEqual(len(xi), 2)
        self.failUnlessEqual(xi[0], 'three')


    def test_toolRolesForPermission(self):
        fgt = getToolByName(self.portal, 'formgen_tool')

        # make sure rolesForPermission works
        roleList = fgt.rolesForPermission('PloneFormGen: Add Content')
        self.failIfEqual(len(roleList), 0)
        mid = ''
        oid = ''
        for role in roleList:
            if role['label'] == 'Manager':
                self.failUnlessEqual(role['checked'], 'CHECKED')
                mid = role['id']
            if role['label'] == 'Owner':
                self.failUnlessEqual(role['checked'], 'CHECKED')
                oid = role['id']
        self.failUnless( mid )
        self.failUnless( oid )

        # let's try changing a permission

        # first, get the request ids
        roleList = fgt.rolesForPermission('PloneFormGen: Edit Advanced Fields')
        self.failIfEqual(len(roleList), 0)
        mid = ''
        oid = ''
        for role in roleList:
            if role['label'] == 'Manager':
                self.failUnlessEqual(role['checked'], 'CHECKED')
                mid = role['id']
            if role['label'] == 'Owner':
                self.failUnlessEqual(role['checked'], None)
                oid = role['id']
        self.failUnless( mid )
        self.failUnless( oid )

        fr = FakeRequest()
        fr.form[mid] = '1'
        fr.form[oid] = '1'
        fr.form['PloneFormGen: Edit Advanced Fields'] = '1'
        fgt.setRolePermits(fr)

        # now, check to see if it took
        roleList = fgt.rolesForPermission('PloneFormGen: Edit Advanced Fields')
        self.failIfEqual(len(roleList), 0)
        mid = ''
        oid = ''
        for role in roleList:
            if role['label'] == 'Manager':
                self.failUnlessEqual(role['checked'], 'CHECKED')
                mid = role['id']
            if role['label'] == 'Owner':
                self.failUnlessEqual(role['checked'], 'CHECKED')
                oid = role['id']
        self.failUnless( mid )
        self.failUnless( oid )
