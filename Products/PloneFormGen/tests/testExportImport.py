#
# Integration tests for interaction with GenericSetup infrastructure
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from transaction import commit
from StringIO import StringIO

from zope.component import getMultiAdapter
from zope.interface import directlyProvides

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import DummyImportContext
from Products.GenericSetup.tests.common import TarballTester

from Products.GenericSetup.context import TarballExportContext
from Products.GenericSetup.interfaces import IFilesystemExporter, IFilesystemImporter

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
    
    def test_profile_form_import(self):
        """We create a profile (see: profiles/testing/structure) 
           which adds a FormFolder called 'test_form_1_' in via our 
           import handler. The form uses the standard ids proceeded by:
           test_form_1_.  We test for the existence of and accurate
           configuration of these subfields below.
        """        
        form_id_prefix = 'test_form_1_'
        form_fields = [{
                        'id':'%sreplyto' % form_id_prefix,
                        'title':'Test Form Your E-Mail Address',},
                       {
                        'id':'%stopic' % form_id_prefix,
                        'title':'Test Form Subject',},
        ]
        field_expressions = {
            '%sreplyto' % form_id_prefix:{'fgTDefault':'here/memberEmail'},
            '%scomments' % form_id_prefix:{'fgDefault': 'string:Test Comment'},
        }
        
        # did our gs form land into the test user's folder
        self.failUnless('%sform-folder' % form_id_prefix in 
            self.folder.objectIds())
        
        # get our forms children to ensure proper config
        gs_form = self.folder['%sform-folder' % form_id_prefix]
        for form_field in form_fields:
            self.failUnless('%s' % form_field['id'] in gs_form.objectIds())
            sub_form_item = gs_form[form_field['id']]
            # make sure all the standard callables are set
            for k,v in form_field.items():
                self.assertEqual(v, getattr(sub_form_item, k))
            # make sure all the expression fields have the correct value
            if field_expressions.has_key(sub_form_item.getId()):
                for k,v in field_expressions[sub_form_item.getId()].items():
                    getattr(sub_form_item,k).text
        
        
        
        


if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExportImport))
    return suite
