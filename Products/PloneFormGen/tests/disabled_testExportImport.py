#
# Integration tests for interaction with GenericSetup infrastructure
#
import os
import re
from tarfile import TarFile
from ZPublisher.HTTPRequest import FileUpload
from cgi import FieldStorage

from StringIO import StringIO

from zope.component import getMultiAdapter

from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import TarballTester

from Products.PloneFormGen.tests import pfgtc
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing.bbb import PTC_FIXTURE
from plone.testing import z2

import Products.PloneFormGen


class TestFormGenGSLayer(PloneSandboxLayer):

    defaultBases = (PTC_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=Products.PloneFormGen)
        self.loadZCML(name="testExportImport.zcml",
                      package=Products.PloneFormGen.tests)
        z2.installProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'Products.PloneFormGen:default')
        self.applyProfile(portal, 'Products.PloneFormGen:testing')


GS_FIXTURE = TestFormGenGSLayer()

GS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GS_FIXTURE,),
    name='Products.PloneFormGen:Integration',
)


class ExportImportTester(pfgtc.PloneFormGenTestCase, TarballTester):
    """Base class for integration test suite for export/import """

    layer = GS_INTEGRATION_TESTING

    def setUp(self):
        super(ExportImportTester, self).setUp()
        # This folder is created by the importer
        self.folder = self.portal.Members.test_user_1_
        self.folder.manage_setLocalRoles(TEST_USER_ID, ["Owner"])

    def _makeForm(self):
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')

    def _prepareFormTarball(self):
        """we could use our @@export-form-folder view,
           but we want a more atomic test, so we make
           a tarfile for our test.  the approach to making
           a tarfile is a bit strange, but does the job
        """
        in_fname = "test_form_1_form-folder.tar.gz"
        test_dir = os.path.dirname(__file__)

        def _add_form_structure_to_archive(archive):
            form_relative_path = os.path.join("profiles", "testing", "structure",
                "Members", "test_user_1_", "test_form_1_form-folder")
            abs_path = os.path.join(test_dir, form_relative_path)

            # add structure folder
            os.chdir(os.path.join(test_dir, "profiles", "testing"))
            archive.add("structure", recursive=False)

            for f in os.listdir(abs_path):
                os.chdir(abs_path) # add form data w/o full directory tree
                archive.add(f, arcname=os.path.join("structure", f))

        # Capture the current working directory for later when we need to
        # clean up the environment.
        working_directory = os.path.abspath(os.curdir)

        # make me a tarfile in the current dir
        os.chdir(test_dir)
        archive = TarFile.open(name=in_fname, mode='w:gz')
        _add_form_structure_to_archive(archive)
        archive.close()

        # Change back to the working directory in case something tries to
        # write files (e.g. collective.xmltestreport).
        os.chdir(working_directory)

        # get it and upload
        in_file = open(os.path.join(test_dir, in_fname))
        env = {'REQUEST_METHOD':'PUT'}
        headers = {'content-type':'text/html',
                   'content-length': len(in_file.read()),
                   'content-disposition':'attachment; filename=%s' % in_file.name}
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
            # XXX andrewb enable when form props are supported
            # 'submitLabel':'Hit Me',
        }

        for k,v in form_values.items():
            self.assertEqual(v, self._extractFieldValue(form_ctx[k]),
                "Expected '%s' for field %s, Got '%s'" % (v, k, form_ctx[k]))

    def _verifyFormStockFields(self, form_ctx, purge):
        """ helper method to verify adherence to profile-based
            form folder in tests/profiles/testing directory
        """
        form_field_ids = form_ctx.objectIds()
        for form_field in ('comments', 'replyto', 'topic', 'mailer', 'thank-you'):
            if purge:
                self.failIf(form_field in form_field_ids,
                    "%s unexpectedly found in %s" % (form_field, form_ctx.getId()))
                continue

            self.failUnless(form_field in form_field_ids,
                "%s not found in %s" % (form_field, form_ctx.getId()))

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
                'useLegend':False,
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
                    val = getattr(sub_form_item, k, sub_form_item[k])
                    # if there is a 'raw' attribute, that's what we want to check
                    val = getattr(val, 'raw', val)
                    # might also be a TALES field, in which case we need
                    # its text attribute
                    val = getattr(val, 'text', val)
                    self.assertEqual(v, val,
                        "Expected '%s' for field %s, Got '%s'" % (v, k, val))


class TestFormExport(ExportImportTester):
    """Export Form Test Suite"""

    file_tmpl = 'structure/%s'
    title_output_tmpl = 'title: %s'

    def _getExporter(self):
        from Products.CMFCore.exportimport.content import exportSiteStructure
        return exportSiteStructure

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

        # make sure our field and adapters are objects
        for id, object in self.ff1.objectItems():
            self.failUnless(form_export_data.has_key(self.file_tmpl % id),
                    "No export representation of %s" % id)
            self.failUnless(self.title_output_tmpl % object.Title() in \
                    form_export_data[self.file_tmpl % id])

        # we should have .properties, .objects, and per subject
        self.assertEqual(len(context._wrote), 2 + len(self.ff1.objectIds()))

    def test_form_properties_contextual_export(self):
        """In order to accurately export the schema values for our
           FormFolder, we forego the otherwise adequate
           StructureFolderWalkingAdapter's ConfigParser format export
           of .properties for favor of an RFC 822  (email) style string
           export.  Confirm that is so here.
        """
        self._makeForm()
        self.ff1.setSubmitLabel("Hit Me")
        context = DummyExportContext(self.ff1)
        exporter = self._getExporter()
        exporter(context)

        # shove everything into a dictionary for easy inspection
        form_export_data = {}
        for filename, text, content_type in context._wrote:
            form_export_data[filename] = text

        ff1_props = form_export_data['structure/.properties']

        lab_pat = re.compile(r'submitLabel.*?Hit Me')
        self.failUnless(lab_pat.search(ff1_props))

    def test_fieldset_properties_contextual_export(self):
        """In order to accurately export the schema values for our
           FieldsetFolder, we forego the otherwise adequate
           StructureFolderWalkingAdapter's ConfigParser format export
           of .properties for favor of an RFC 822 (email) style string
           export.  Confirm that is so here.
        """
        self._makeForm()
        self.ff1.invokeFactory('FieldsetFolder','fsf1')
        self.ff1.fsf1.setTitle('FormFolder1 FieldsetFolder1')
        self.ff1.fsf1.setUseLegend(False) # set a non-default value
        context = DummyExportContext(self.ff1)
        exporter = self._getExporter()
        exporter(context)

        # shove everything into a dictionary for easy inspection
        form_export_data = {}
        for filename, text, content_type in context._wrote:
            form_export_data[filename] = text

        fsf1_props = form_export_data['structure/fsf1/.properties']

        self.failUnless('FormFolder1 FieldsetFolder1' in fsf1_props)
        leg_pat = re.compile(r'useLegend.*?False')
        self.failUnless(leg_pat.search(fsf1_props))

    def test_stock_form_view_export(self):
        """We provide a browser view that can be used to
           export a given form as the root context as well.
           XXX - Andrew B remember this is a rather tempoary representation
                 of what's returned.
        """
        toc_list = ['structure/.objects', 'structure/.properties', 'structure/mailer',
                    'structure/replyto', 'structure/topic', 'structure/comments',
                    'structure/thank-you']
        self._makeForm()
        form_folder_export = getMultiAdapter((self.folder.ff1, self.app.REQUEST),
                                              name='export-form-folder')
        fileish = StringIO( form_folder_export() )
        try:
            self._verifyTarballContents( fileish, toc_list)
        except AssertionError:
            toc_list.append('structure')
            self._verifyTarballContents( fileish, toc_list)


class TestFormImport(ExportImportTester):
    """Import Form Test Suite"""
    def _getImporter(self):
        from Products.CMFCore.exportimport.content import importSiteStructure
        return importSiteStructure

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
        request = self.app.REQUEST
        request.form={
            'form.upload':self._prepareFormTarball(),
            'form.actions.import':'import'}
        request.RESPONSE = request.response

        # get the form object
        import_form = getMultiAdapter((self.ff1, request), name='import-form-folder')

        # call update (aka submit) on the form, see TestRequest above
        import_form.update()
        self._verifyProfileForm(self.ff1)
        self._verifyFormStockFields(self.ff1, purge=False)

    def test_formlib_form_with_purge_import(self):
        self._makeForm()

        # submit the form requesting purge of contained fields
        request = self.app.REQUEST
        request.form={
            'form.purge':u'on',
            'form.upload':self._prepareFormTarball(),
            'form.actions.import':'import'}
        request.RESPONSE = self.app.REQUEST.response

        # get the form object
        import_form = getMultiAdapter((self.ff1, request), name='import-form-folder')

        # call update (aka submit) on the form, see TestRequest above
        import_form.update()
        self._verifyProfileForm(self.ff1)
        self._verifyFormStockFields(self.ff1, purge=True)
