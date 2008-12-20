#
# Integration tests for interaction with GenericSetup infrastructure
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# from tarfile import TarFile
from ZPublisher.HTTPRequest import FileUpload
from cgi import FieldStorage

from transaction import commit
from StringIO import StringIO

from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import TarballTester

from Products.PloneFormGen.tests import pfgtc

from Testing import ZopeTestCase
from Products.PloneTestCase.layer import PloneSite

zcml_string = """\
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:gs="http://namespaces.zope.org/genericsetup"
           package="Products.PloneFormGen">

    <gs:registerProfile
        name="testing"
        title="PloneFormGen testing"
        description="Used for testing only" 
        directory="tests/profiles/testing"
        for="Products.CMFPlone.interfaces.IPloneSiteRoot"
        provides="Products.GenericSetup.interfaces.EXTENSION"
        />
        
</configure>
"""

class TestFormGenGSLayer(PloneSite):
    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        zcml.load_string(zcml_string)
        fiveconfigure.debug_mode = False
        
        app = ZopeTestCase.app()
        portal = app.plone
        
        # elevate permissions
        from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
        user = portal.getWrappedOwner()
        newSecurityManager(None, user)
        
        portal_setup = portal.portal_setup
        portal_setup.runAllImportStepsFromProfile('profile-Products.PloneFormGen:testing')
        
        # drop elevated perms
        noSecurityManager()
        
        commit()
        ZopeTestCase.close(app)

class TestExportImport(pfgtc.PloneFormGenTestCase, TarballTester):
    """Integration test suite for export/import """
    
    layer = TestFormGenGSLayer
    
    def _makeForm(self):
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
    
    def _prepareFormTarball(self):
        # we could use our @@export-form-folder view, 
        # but we want a more atomic test, so we make
        # a tarfile for our test
        in_fname = 'test_form_1_form-folder.tar.gz'
        
        # XXX - Clean-up
        # in_fpath = os.path.join(os.path.dirname(__file__),'profiles', 'testing', 'structure', 
        #     'Members', 'test_user_1_', 'test_form_1_form-folder')
        # archive = TarFile.open(in_fname, 'w:gz')
        # archive.add(in_fpath)
        # archive.close()
        
        in_file = open(os.path.join(os.path.dirname(__file__), in_fname))
        env = {'REQUEST_METHOD':'PUT'}
        headers = {'content-type':'text/html',
                   'content-length': len(in_file.read()),
                   'content-disposition':'attachment; filename=%s' % in_fname}
        in_file.seek(0)
        fs = FieldStorage(fp=in_file, environ=env, headers=headers)
        return FileUpload(fs)
    
    def _extractFieldValue(self, setval):
        """differentiate datastructure for TALESField instances vs.
           standard ATField instances
        """
        if hasattr(setval, 'raw'):
            setval = setval.raw
        
        return setval
    
    def _verifyProfileFormSettings(self, form_ctx):
        form_values = {
            'title':'My OOTB Form',
            #'isDiscussable':False,
            'description':'The description for our OOTB form',
        }
        
        for k,v in form_values.items():
            self.assertEqual(v, self._extractFieldValue(form_ctx[k]),
                "Expected '%s' for field %s, Got '%s'" % (v, k, form_ctx[k]))
    
    def _verifyProfileForm(self, form_ctx, form_fields=None):
        """ helper method to verify adherence to profile-based
            form folder in tests/profiles/testing directory
        """
        form_id_prefix = 'test_form_1_'
        
        if not form_fields:
            form_fields = [
               {
                'id':'%sreplyto' % form_id_prefix,
                'title':'Test Form Your E-Mail Address',
                'required':True,
                #'isDiscussable':False,
                'fgTDefault':'here/memberEmail',},
               {
                'id':'%shidden' % form_id_prefix,
                'title':'This is a sample hidden field',
                'required':False,
                #'isDiscussable':False,
                'hidden':True,},
               {
                'id':'%sfieldset-folder' % form_id_prefix,
                'title':'Fields grouped in a fieldset',
                'subfields':[{
                    'id':'%shidden_fieldset' % form_id_prefix,
                    'title':'This is a sample hidden field fieldset',
                    'required':True,
                    #'isDiscussable':False,
                    'hidden':True,
                },],},
               {
                'id':'%stopic' % form_id_prefix,
                'title':'Test Form Subject',
                # 'isDiscussable':False,
                'required':True,},
               {
                'id':'%scomments' % form_id_prefix,
                'fgDefault': 'string:Test Comment',},
            ]
        
        # get our forms children to ensure proper config
        for form_field in form_fields:
            self.failUnless('%s' % form_field['id'] in form_ctx.objectIds())
            sub_form_item = form_ctx[form_field['id']]
            # make sure all the standard callables are set
            for k,v in form_field.items():
                if k == 'subfields':
                    self._verifyProfileForm(sub_form_item, v)
                else:
                    self.assertEqual(v, self._extractFieldValue(sub_form_item[k]),
                        "Expected '%s' for field %s, Got '%s'" % (v, k, sub_form_item[k]))
    
    def _getExporter(self):
        from Products.CMFCore.exportimport.content import exportSiteStructure
        return exportSiteStructure
    
    def _getImporter(self):
        from Products.CMFCore.exportimport.content import importSiteStructure
        return importSiteStructure
    
    def test_stock_form_contextual_export(self):
        """Upon adding a form folder, we're given a fully functional
           example form that provides several fields, a mailer, and 
           a thanks page.  Let's make sure a contextual export includes what
           we're expecting.
        """
        self._makeForm()
        context = DummyExportContext(self.ff1)
        exporter = self._getExporter()
        exporter(context)
        
        # shove everything into a dictionary for easy inspection
        form_export_data = {}
        for filename, text, content_type in context._wrote:
            form_export_data[filename] = text
        
        file_tmpl = 'structure/%s'
        title_output_tmpl = 'title: %s'
        
        # make sure our field and adapters are objects
        for id, object in self.ff1.objectItems():
            self.failUnless(form_export_data.has_key(file_tmpl % id), 
                    "No export representation of %s" % id)
            self.failUnless(title_output_tmpl % object.Title() in \
                    form_export_data[file_tmpl % id])
        
        # we should have .properties, .objects, and per subject
        self.assertEqual(len(context._wrote), 2 + len(self.ff1.objectIds()))
    
    def test_stock_form_view_export(self):
        """We provide a browser view that can be used to 
           export a given as the root context as well.  
           XXX - Andrew B remember this is a rather tempoary representation
                 of what's returned.
        """
        toc_list = ['structure/.objects', 'structure/.properties', 'structure/mailer', 
                    'structure/replyto', 'structure/topic', 'structure/comments', 
                    'structure/thank-you']
        self._makeForm()
        form_folder_export = self.folder.ff1.restrictedTraverse('@@export-form-folder')
        fileish = StringIO( form_folder_export() )
        self._verifyTarballContents( fileish, toc_list)
    
    def test_form_values_from_gs_import(self):
        """We provide a custom IFilesystemImporter so that
           all the schema fields from a configured FormFolder
           land in the imported form.
        """
        self.failUnless('test_form_1_form-folder' in self.folder.objectIds())
        self._verifyProfileFormSettings(self.folder['test_form_1_form-folder'])
    
    def test_profile_from_gs_import(self):
        """We create a profile (see: profiles/testing/structure) 
           which adds a FormFolder called 'test_form_1_' in via our 
           import handler. The form uses the standard ids proceeded by:
           test_form_1_.  We test for the existence of and accurate
           configuration of these subfields below.
        """        
        # did our gs form land into the test user's folder
        self.failUnless('test_form_1_form-folder' in self.folder.objectIds())
        self._verifyProfileForm(self.folder['test_form_1_form-folder'])
    
    def test_formlib_form_import(self):
        """Interacting with our formlib form we should be able
           to successfully upload an exported PFG form and have it
           correctly configured.
        """
        self._makeForm()
        
        # setup a reasonable request
        request = TestRequest(form={
            'form.upload':self._prepareFormTarball(),
            'form.actions.import':'import'})
        request.RESPONSE = request.response
        
        # get the form object
        import_form = getMultiAdapter((self.ff1, request), name='import-form-folder')
        
        # call update (aka submit) on the form, see TestRequest above
        import_form.update()
        self._verifyProfileForm(self.ff1)
    

if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExportImport))
    return suite
