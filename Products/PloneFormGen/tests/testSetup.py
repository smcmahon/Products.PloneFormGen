#
# Test PloneFormGen initialisation and set-up
#
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.PloneFormGen.tests import pfgtc
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import Products


def getAddPermission(product, name):
    """ find the add permission for a meta_type """

    name = "%s: %s" % (product, name)
    for mt in Products.meta_types:
        if mt['name'] == name:
            return mt['permission']
    return ""


class TestInstallation(pfgtc.PloneFormGenTestCase):
    """Ensure product is properly installed"""

    def setUp(self):
        pfgtc.PloneFormGenTestCase.setUp(self)

        self.kupu         = getattr(self.portal, 'kupu_library_tool', None)
        self.skins        = self.portal.portal_skins
        self.types        = self.portal.portal_types
        self.factory      = self.portal.portal_factory
        self.workflow     = self.portal.portal_workflow
        self.properties   = self.portal.portal_properties
        self.at_tool      = self.portal.archetype_tool
        self.controlpanel = self.portal.portal_controlpanel

        fieldTypes = [
            'FormSelectionField',
            'FormMultiSelectionField',
            'FormLabelField',
            'FormDateField',
            'FormLinesField',
            'FormIntegerField',
            'FormBooleanField',
            'FormPasswordField',
            'FormFixedPointField',
            'FormStringField',
            'FormTextField',
            'FormRichTextField',
            'FormRichLabelField',
            'FormFileField',
            'FormLikertField',
        ]
        if pfgtc.haveRecaptcha:
            fieldTypes.append('FormCaptchaField')
        self.fieldTypes = tuple(fieldTypes)
        self.adapterTypes = (
            'FormSaveDataAdapter',
            'FormMailerAdapter',
            'FormCustomScriptAdapter',
        )
        self.thanksTypes = (
            'FormThanksPage',
        )
        self.fieldsetTypes = (
            'FieldsetFolder',
        )
        self.metaTypes = ('FormFolder',) + self.fieldTypes + self.adapterTypes + self.thanksTypes + self.fieldsetTypes

    def testSkinLayersInstalled(self):
        self.failUnless('PloneFormGen' in self.skins.objectIds())

    def testSkinLayersInSkinPath(self):
        pfg_layers = self.skins['PloneFormGen']
        for skin_name, obj in pfg_layers.items():
            self.failUnless('PloneFormGen' in obj.getPhysicalPath())

    def testKssRegsitry(self):
        if 'portal_kss' in self.portal.objectIds():
            # confirm kinetic stylesheet registration
            for kss_id in ('ploneformgen.kss',):
                self.failUnless(kss_id in self.portal.portal_kss.getResourceIds(),
                    "The kss resource %s wasn't registered appropriately with the portal_kss registry")

    def testTypesInstalled(self):
        for t in self.metaTypes:
            self.failUnless(t in self.types.objectIds())

    def testTypeActions(self):
        # hide properties/references tabs
        for typ in self.metaTypes:
            for act in self.types[typ].listActions():
                if act.id in ['metadata', 'references']:
                    self.failIf(act.visible)

    def testArchetypesToolCatalogRegistration(self):
        for t in self.metaTypes:
            self.assertEquals(1, len(self.at_tool.getCatalogsByType(t)))
            self.assertEquals('portal_catalog', self.at_tool.getCatalogsByType(t)[0].getId())

    def testControlPanelConfigletInstalled(self):
        self.failUnless('PloneFormGen' in [action.id for action in self.controlpanel.listActions()])

    def testAddPermissions(self):
        """ Test to make sure add permissions are as intended """

        ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Content'
        CSA_ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Custom Scripts'
        MA_ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Mailers'
        SDA_ADD_CONTENT_PERMISSION = 'PloneFormGen: Add Data Savers'

        self.assertEqual( getAddPermission('PloneFormGen', 'Form Folder'), ADD_CONTENT_PERMISSION)
        self.assertEqual( getAddPermission('PloneFormGen', 'Mailer Adapter'), MA_ADD_CONTENT_PERMISSION)
        self.assertEqual( getAddPermission('PloneFormGen', 'Save Data Adapter'), SDA_ADD_CONTENT_PERMISSION)
        self.assertEqual( getAddPermission('PloneFormGen', 'Custom Script Adapter'), CSA_ADD_CONTENT_PERMISSION)

    def testActionsInstalled(self):
        self.setRoles(['Manager',])
        self.failUnless(self.portal.portal_actions.getActionInfo('object_buttons/export'))
        self.failUnless(self.portal.portal_actions.getActionInfo('object_buttons/import'))

    def testPortalFactorySetup(self):
        for f in self.metaTypes:
            self.failUnless(f in self.factory.getFactoryTypes())

    def testTypesNotSearched(self):
        types_not_searched = self.properties.site_properties.getProperty('types_not_searched')
        for f in self.fieldTypes + self.adapterTypes + self.thanksTypes + self.fieldsetTypes:
            self.failUnless(f in types_not_searched)

    def testTypesNotListed(self):
        metaTypesNotToList  = self.properties.navtree_properties.getProperty('metaTypesNotToList')
        for f in self.fieldTypes + self.adapterTypes + self.thanksTypes + self.fieldsetTypes:
            self.failUnless(f in metaTypesNotToList)

    def testFieldsHaveNoWorkflow(self):
        for f in self.fieldTypes + self.fieldsetTypes:
            self.assertEqual(self.workflow.getChainForPortalType(f), ())

    def testAdaptersHaveNoWorkflow(self):
        for f in self.adapterTypes:
            self.assertEqual(self.workflow.getChainForPortalType(f), ())

    def testThankspagessHaveNoWorkflow(self):
        for f in self.thanksTypes:
            self.assertEqual(self.workflow.getChainForPortalType(f), ())

    def testKupuResources(self):
        if self.kupu is not None:
            linkable = self.kupu.getPortalTypesForResourceType('linkable')
            self.failUnless('FormFolder' in linkable) # make sure we made it in ...
            self.failIf(len(linkable) <= 1) # without clobbering everything else

    def test_FormGenTool(self):
        self.failUnless( getToolByName(self.portal, 'formgen_tool'))

    def test_PropSheetCreation(self):
        props = getattr(self.properties, 'ploneformgen_properties', None)
        self.failUnless( props )
        self.failUnless( props.hasProperty('permissions_used') )
        self.failUnless( props.hasProperty('mail_template') )
        self.failUnless( props.hasProperty('mail_body_type') )
        self.failUnless( props.hasProperty('mail_recipient_email') )
        self.failUnless( props.hasProperty('mail_cc_recipients') )
        self.failUnless( props.hasProperty('mail_bcc_recipients') )
        self.failUnless( props.hasProperty('mail_xinfo_headers') )
        self.failUnless( props.hasProperty('mail_add_headers') )
        self.failUnless( props.hasProperty('csv_delimiter') )

    def testModificationsToPropSheetNotOverwritten(self):
        newprop = 'foo'
        self.properties.ploneformgen_properties.manage_changeProperties(mail_body_type=newprop)

        # reinstall
        qi = self.portal.portal_quickinstaller
        qi.reinstallProducts(['PloneFormGen'])

        # make sure we still have our new value for 'mail_body_type'
        self.assertEquals(newprop, self.properties.ploneformgen_properties.getProperty('mail_body_type'))

    def testModificationsToRegistryLinesNotPurged(self):
        registry = getUtility(IRegistry)
        settings = [
            'plone.default_page_types',
        ]

        # add garbage prop element to each lines property
        for option in settings:
            value = registry[option]
            if isinstance(value, tuple):
                value = list(value)
                value.append(u'foo')
                value = tuple(value)
            else:
                value.append(u'foo')
            registry[option] = value

        # reinstall
        qi = self.portal.portal_quickinstaller
        qi.reinstallProducts(['PloneFormGen'])

        # now make sure our garbage values survived the reinstall
        for option in settings:
            self.failUnless(
                u'foo' in registry[option],
                "Our garbage item didn't survive reinstall for property %s" %
                option)

    def test_FormFolderInDefaultPageTypes(self):
        registry = getUtility(IRegistry)
        defaultPageTypes = registry['plone.default_page_types']
        self.failUnless('FormFolder' in defaultPageTypes)

    def testTypeViews(self):
            self.assertEqual(self.types.FormFolder.getAvailableViewMethods(self.types), ('fg_base_view_p3',))
            self.assertEqual(self.types.FormThanksPage.getAvailableViewMethods(self.types), ('fg_thankspage_view_p3',))
            self.assertEqual(self.types.FormSaveDataAdapter.getAvailableViewMethods(self.types), ('fg_savedata_tabview_p3', 'fg_savedata_recview_p3', 'fg_savedata_view_p3'))



class TestContentCreation(pfgtc.PloneFormGenTestCase):
    """Ensure content types can be created and edited"""

    fieldTypes = [
        'FormSelectionField',
        'FormMultiSelectionField',
        'FormLabelField',
        'FormDateField',
        'FormLinesField',
        'FormIntegerField',
        'FormBooleanField',
        'FormPasswordField',
        'FormFixedPointField',
        'FormStringField',
        'FormTextField',
        'FormRichTextField',
        'FormFileField',
    ]
    if pfgtc.haveRecaptcha:
        fieldTypes.append('FormCaptchaField')
    fieldTypes = tuple(fieldTypes)

    adapterTypes = (
        'FormSaveDataAdapter',
        'FormMailerAdapter',
    )

    thanksTypes = (
        'FormThanksPage',
    )

    fieldsetTypes = (
        'FieldsetFolder',
    )

    sampleContentIds = ('mailer', 'replyto', 'topic', 'comments', 'thank-you')


    def setUp(self):
        pfgtc.PloneFormGenTestCase.setUp(self)
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')

    def testCreateFormFolder(self):
        self.failUnless('ff1' in self.folder.objectIds())

    def testSampleContent(self):
        # check embedded content
        oi = self.ff1.objectIds()
        for id in self.sampleContentIds:
            self.failUnless(id in oi)

    def testSampleMailerSetup(self):
        self.assertEqual(self.ff1.actionAdapter, ('mailer',))
        self.assertEqual(self.ff1.mailer.replyto_field, 'replyto')
        self.assertEqual(self.ff1.mailer.subject_field, 'topic')
        self.assertEqual(self.ff1.mailer.thanksPage, 'thank-you')

    def testFormFolderCanSetDefaultPage(self):
        self.assertEqual(self.ff1.canSetDefaultPage(), False)

    def testEditFormFolder(self):
        self.ff1.setTitle('A title')
        self.ff1.setDescription('A description')

        self.assertEqual(self.ff1.Title(), 'A title')
        self.assertEqual(self.ff1.Description(), 'A description')

    def testCreateFields(self):
        for f in self.fieldTypes:
            fname = "%s1" % f
            self.ff1.invokeFactory(f, fname)
            self.failUnless(fname in self.ff1.objectIds())

    def testCreateAdapters(self):
        for f in self.adapterTypes:
            fname = "%s1" % f
            self.ff1.invokeFactory(f, fname)
            self.failUnless(fname in self.ff1.objectIds())
            self.failUnless(hasattr(self.ff1[fname], 'onSuccess'))

    def testCreateThanksPages(self):
        for f in self.thanksTypes:
            fname = "%s1" % f
            self.ff1.invokeFactory(f, fname)
            self.failUnless(fname in self.ff1.objectIds())
            self.failUnless(hasattr(self.ff1[fname], 'displayFields'))

    def testCreateFieldset(self):
        for f in self.fieldsetTypes:
            fname = "%s1" % f
            self.ff1.invokeFactory(f, fname)
            self.failUnless(fname in self.ff1.objectIds())

    def testCreateFieldsinFieldset(self):
        fname = 'FieldsetFolder1'
        self.ff1.invokeFactory('FieldsetFolder', fname)
        self.failUnless(fname in self.ff1.objectIds())
        fs = self.ff1[fname]
        for f in self.fieldTypes:
            fname = "%s1fs" % f
            fs.invokeFactory(f, fname)
            self.failUnless(fname in fs.objectIds())

        # Things that shouldn't fit in a fieldset folder
        self.assertRaises(ValueError, fs.invokeFactory, 'FormFolder', 'ffinf')
        self.assertRaises(ValueError, fs.invokeFactory, 'FormThanksPage', 'ffinf')
        self.assertRaises(ValueError, fs.invokeFactory, 'FieldsetFolder', 'ffinf')
        self.assertRaises(ValueError, fs.invokeFactory, 'FormMailerAdapter', 'ffinf')

        # try finding the fields
        for f in self.fieldTypes:
            fname = "%s1fs" % f
            self.failUnless( self.ff1.findFieldObjectByName(fname) )


    def testFgFieldsDisplayOnly(self):
        """ Make sure fgFields displayOnly parameter correctly excludes
            labels and fieldset markers
        """

        noExtras = len(self.ff1.fgFields(displayOnly=True))
        wExtras = len(self.ff1.fgFields())
        self.failUnlessEqual(wExtras, noExtras)

        self.ff1.invokeFactory('FieldsetFolder', 'FieldsetFolder1')
        self.ff1['FieldsetFolder1'].invokeFactory('FormStringField', 'fsf')

        noExtras = len(self.ff1.fgFields(displayOnly=True))
        wExtras = len(self.ff1.fgFields())
        self.failUnlessEqual(wExtras, noExtras+2)

        self.ff1.invokeFactory('FormLabelField', 'flf')
        noExtras = len(self.ff1.fgFields(displayOnly=True))
        wExtras = len(self.ff1.fgFields())
        self.failUnlessEqual(wExtras, noExtras+3)

        self.ff1.invokeFactory('FormRichLabelField', 'frlf')
        noExtras = len(self.ff1.fgFields(displayOnly=True))
        wExtras = len(self.ff1.fgFields())
        self.failUnlessEqual(wExtras, noExtras+4)


    def testEditField(self):
        for f in self.fieldTypes:
            fname = "%s1" % f
            self.ff1.invokeFactory(f, fname)
            f1 = getattr(self.ff1, fname)
            f1.setTitle('Field title')
            f1.setDescription('Field description')

            self.assertEqual(f1.Title(), 'Field title')
            self.assertEqual(f1.fgField.widget.label, 'Field title')
            self.assertEqual(f1.Description(), 'Field description')
            self.assertEqual(f1.fgField.widget.description, 'Field description')

    def testTALESFieldValidation(self):
        for f in self.fieldTypes:
            if f != 'FormLabelField':
                fname = "%s1" % f
                self.ff1.invokeFactory(f, fname)
                f1 = getattr(self.ff1, fname)
                self.assertEqual(f1.getFgTValidator(), False)
                f1.setFgTValidator('python:True')
                self.assertEqual(f1.getFgTValidator(), True)

    def testEditAdapter(self):
        for f in self.adapterTypes:
            fname = "%s1" % f
            self.ff1.invokeFactory(f, fname)
            f1 = getattr(self.ff1, fname)
            f1.setTitle('title')
            f1.setDescription('description')

            self.assertEqual(f1.Title(), 'title')
            self.assertEqual(f1.Description(), 'description')

    def testMailerZPTBody(self):
        fname = 'FormMailerAdapter1'
        self.ff1.invokeFactory('FormMailerAdapter', fname)
        f1 = getattr(self.ff1, fname)
        self.failUnless( f1.getBody_pt(fields=[], wrappedFields=[]) )

    def testEditThanksPages(self):
        for f in self.thanksTypes:
            fname = "%s1" % f
            self.ff1.invokeFactory(f, fname)
            f1 = getattr(self.ff1, fname)
            f1.setTitle('title')
            f1.setDescription('description')

            self.assertEqual(f1.Title(), 'title')
            self.assertEqual(f1.Description(), 'description')

    def testCreateFieldsAdaptersOutsideFormFolder(self):
        for f in self.fieldTypes + self.adapterTypes + self.thanksTypes + self.fieldsetTypes:
            try:
                self.folder.invokeFactory(f, 'f1')
            except (Unauthorized, ValueError):
                return
            self.fail('Expected error when creating form field or adapter outside form folder.')

    def testBadIdField(self):
        # test for tracker #32 - Field with id 'language' causes problems with PTS

        from Products.CMFCore.exceptions import BadRequest

        fname = 'test_field'
        self.ff1.invokeFactory('FormStringField', fname)
        f1 = getattr(self.ff1, fname)

        self.assertRaises(BadRequest, f1.setId, 'language')

        # also not such a good idea ...
        self.assertRaises(BadRequest, f1.setId, 'form')


    def testFieldRename(self):
        """
        renaming a field should change the __name__ attribute
        of the embedded fgField; tracker issue #42
        """

        self.ff1.invokeFactory('FormStringField', 'spam_and_eggs')
        self.failUnless('spam_and_eggs' in self.ff1.objectIds())

        myField = getattr(self.ff1, 'spam_and_eggs')
        fgf = getattr(myField, 'fgField')
        self.assertEqual(fgf.__name__, 'spam_and_eggs')

        # XXX TODO: figure out what's wrong with this:
        #self.ff1.manage_renameObject('spam_and_eggs', 'spam_spam_and_eggs')
        #self.assertEqual(fgf.__name__, 'spam_spam_and_eggs')


    def testFieldsetRename(self):
        """
        renaming a fieldset should change the __name__ attribute
        of the embedded fsStartField
        """

        self.ff1.invokeFactory('FieldsetFolder', 'fsfolder1')
        self.failUnless('fsfolder1' in self.ff1.objectIds())

        myField = getattr(self.ff1, 'fsfolder1')
        fgf = getattr(myField, 'fsStartField')
        self.assertEqual(fgf.__name__, 'fsfolder1')


    def testFieldsetPlusDisplayList(self):
        """ Test for issue  #44 -- Presence of fieldset causes an attribute error
        """

        # create fieldset
        self.ff1.invokeFactory('FieldsetFolder', 'fsf1')
        self.failUnless( self.ff1.fgFieldsDisplayList() )


    def testUtfInFieldTitle(self):
        """ test for issue # 102, 104: utf8, non-ascii in field title or description
        """

        self.ff1.invokeFactory('FormStringField', 'sf1',
         title='Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'.decode('utf-8'))

        self.ff1.sf1.setDescription( 'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'.decode('utf-8') )
        # force a reindex
        self.ff1.sf1.reindexObject()


    def testUtfInFormTitle(self):
        """ test for utf8, non-ascii in form title or description
        """

        self.folder.invokeFactory('FormFolder', 'ff2',
         title='Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'.decode('utf-8'))

        self.folder.ff2.setDescription( 'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'.decode('utf-8') )
        # force a reindex
        self.folder.ff2.reindexObject()

    def testBadIds(self):
        """ test ids that cause problems.
            We shouldn't be able to create objects with ids known
            to be troublesome.
            Also, all fields in all fieldsets must have unique ids.
        """

        # should be OK:
        self.failUnless( self.ff1.checkIdAvailable('somethingunique8723') )

        # bad ids should fail
        self.failIf( self.ff1.checkIdAvailable('zip') )
        self.failIf( self.ff1.checkIdAvailable('location') )
        self.failIf( self.ff1.checkIdAvailable('language') )

        # existing ids should fail
        self.ff1.invokeFactory('FormStringField', 'sf1')
        self.failIf( self.ff1.checkIdAvailable('sf1') )

        # test in fieldset folder
        self.ff1.invokeFactory('FieldsetFolder', 'fsf1')
        fsf1 = self.ff1.fsf1
        self.failUnless( fsf1.checkIdAvailable('somethingunique8723') )
        self.failIf( fsf1.checkIdAvailable('zip') )

        # We should also not be able to create a fieldset folder field
        # with an id the same as one in the parent form folder
        self.failIf( fsf1.checkIdAvailable('sf1') )
        # nor in the fieldset folder itself
        fsf1.invokeFactory('FormStringField', 'sf2')
        self.failIf( fsf1.checkIdAvailable('sf2') )

        # Let's try it in a sibling fieldset folder
        self.ff1.invokeFactory('FieldsetFolder', 'fsf2')
        fsf2 = self.ff1.fsf2
        self.failUnless( fsf2.checkIdAvailable('somethingunique8723') )
        self.failIf( fsf2.checkIdAvailable('sf1') )
        self.failIf( fsf2.checkIdAvailable('sf2') )


class TestGPG(pfgtc.PloneFormGenTestCase):
    """ test ya_gpg.py """

    def test_gpg(self):
        from Products.PloneFormGen.content.ya_gpg import gpg, GPGError

        if gpg is None:
            print "\nSkipping GPG tests; gpg binary not found"
        else:
            self.assertRaises(GPGError, gpg.encrypt, 'spam', 'eggs')
