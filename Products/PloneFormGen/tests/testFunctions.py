# -*- coding: utf-8 -*-
#
# Integration tests. See other test modules for specific components.
#
import sys
import plone.protect

from Products.PloneFormGen.tests import pfgtc

from Testing.makerequest import makerequest
import zExceptions
from zope.component import getMultiAdapter

from plone.protect.authenticator import AuthenticatorView


# too lazy to see if this is already in the library somewhere
def stripWhiteSpace(multiLineString):
    return '\n'.join([s.strip() for s in multiLineString.split('\n')])

class TestFunctions(pfgtc.PloneFormGenTestCase):
    """ tests that mostly concern functionality beyond the unit """

    def dummy_send( self, mfrom, mto, messageText, immediate=False ):
        self.mfrom = mfrom
        self.mto = mto
        self.messageText = messageText


    def fakeRequest(self, **kwargs):
        self.request.form.clear()
        self.request._authenticator = plone.protect.createToken()
        self.request.form.update(kwargs)
        self.request.form['_authenticator'] = self.request._authenticator
        return self.request


    def setUp(self):
        pfgtc.PloneFormGenTestCase.setUp(self)
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        self.mailhost = self.folder.MailHost
        self.mailhost._send = self.dummy_send
        self.ff1.mailer.setRecipient_email('mdummy@address.com')
        self.request = makerequest(self.app).REQUEST
        self.ff1.checkAuthenticator = False


    def testFgFieldsDisplayList(self):
        """ test Form Folder's fgFieldsDisplayList """

        # in v 1.0.2, this caused "'unicode' object has no attribute 'decode'" w/ Plone 2.5.1 and Zope 2.8.7
        res = self.ff1.fgFieldsDisplayList()

        self.assertEqual(len(res), 3)
        self.assertEqual( res.keys()[0], 'replyto' )
        self.failUnless( isinstance(res.values()[0], unicode) )


    def testFgFieldsDisplayListFieldset(self):
        """ Make sure fgFieldsDisplayList works for fields in fieldsets.
            Tracker #123.
        """

        self.ff1.invokeFactory('FieldsetFolder', 'fsf1', title='a fieldset')
        fsf1 = self.ff1.fsf1
        fsf1.invokeFactory('FormStringField', 'fsf', title='a string field')

        res = self.ff1.fgFieldsDisplayList(objTypes=['FormStringField'])
        self.assertEqual(len(res), 3)

        res = self.ff1.mailer.fieldsDisplayList()
        self.assertEqual(len(res), 4)


    def testFgFieldsDisplayOnly(self):
        """ test Form Folder's fgFields displayOnly option """

        ff = self.ff1
        len1 = len(ff.fgFields())

        ff.invokeFactory('FormLabelField', 'lf')
        ff.invokeFactory('FormRichLabelField', 'rlf')

        # when displayOnly==True, fgFields should not return label fields
        self.assertEqual(len(ff.fgFields(displayOnly=True)), len1)
        # when displayOnly is omitted, all fields should be returned
        self.assertEqual(len(ff.fgFields()), len1+2)


    def test_Validate(self):
        """ Test required field validation """

        request = self.fakeRequest(topic = 'test subject')

        errors = self.ff1.fgvalidate(REQUEST=request)
        self.failUnless( errors['replyto'] )
        self.failUnless( errors['comments'] )
        self.failUnless( errors.get('topic') is None )

        request = self.fakeRequest(topic = 'test subject', replyto='testtest.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.failUnless( errors['replyto'] )

        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )

        # since that should have validated, it should have been mailed
        self.failUnless( self.messageText.find('Reply-To: test@test.org') > 0 )


    def test_selfValidate(self):
        """ Test field self validation """

        request = self.fakeRequest(topic = 'test subject ')
        errors = self.ff1.topic.fgvalidate(request)
        self.assertEqual( errors, {} )


    def test_i18nTitleValidate(self):
        """ Test field self validation with required non-ASCII field title """

        self.ff1.topic.setTitle('Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es')
        request = self.fakeRequest()
        errors = self.ff1.topic.fgvalidate(request)
        self.failUnless( errors.has_key('topic') )


    def test_CustomValidation(self):
        """ test to make sure the custom TALES validation works
        """

        # test in field context (field validating itself)

        # make sure it fails when test is invalid
        request = self.fakeRequest(topic = 'test subject ')
        self.ff1.topic.setFgTValidator( 'python: 1/0' )
        self.assertRaises(ZeroDivisionError, self.ff1.topic.fgvalidate, request)

        # now for a more realistic custom validator
        self.ff1.topic.setFgTValidator( 'python: test(value.find("test") >= 0, 0, "test is missing")' )

        request = self.fakeRequest(topic = 'test subject ')
        errors = self.ff1.topic.fgvalidate(request)
        self.assertEqual( errors, {} )

        request = self.fakeRequest(topic = 'no subject ')
        errors = self.ff1.topic.fgvalidate(request)
        self.failUnless( errors['topic'] == 'test is missing' )

        # also check in form context (form validating field)

        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )

        request = self.fakeRequest(topic = 'no subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.failUnless( errors['topic'] == 'test is missing' )



    def testHtmlValue(self):
        """ Test field htmlValue method """

        request = self.fakeRequest(topic = 'test subject')
        self.assertEqual( self.ff1['topic'].htmlValue(request), 'test subject')

        # check utf-8 encoded
        request = self.fakeRequest(topic = 'test \xc3\x91 subject')
        self.assertEqual( self.ff1['topic'].htmlValue(request), 'test \xc3\x91 subject')

        # check unicode
        request = self.fakeRequest(topic = u'test \xd1 subject')
        self.assertEqual( self.ff1['topic'].htmlValue(request), 'test \xc3\x91 subject')

        # test html escaping
        request = self.fakeRequest(topic = 'test < & > subject')
        self.assertEqual( self.ff1['topic'].htmlValue(request), 'test &lt; &amp; &gt; subject')

        # test list cleanup
        request = self.fakeRequest(topic = ['one'])
        self.assertEqual( self.ff1['topic'].htmlValue(request), "'one'")

        # test list cleanup with mixed values
        request = self.fakeRequest(topic = ['test \xc3\x91 subject', u'test \xd1 subject', 1])
        self.assertEqual( self.ff1['topic'].htmlValue(request), "'test \\xc3\\x91 subject', 'test \\xc3\\x91 subject', 1")

        # test non-list non-cleanup
        request = self.fakeRequest(topic = "['one',]")
        self.assertEqual( self.ff1['topic'].htmlValue(request), "['one',]")

        # test eol encoding
        request = self.fakeRequest(comments = "one\ntwo")
        self.assertEqual( self.ff1['comments'].htmlValue(request), '<div>one<br />two</div>')


    def testHtmlValueSelectionField(self):
        """ Test field htmlValue method of selection field """

        self.ff1.invokeFactory('FormSelectionField', 'fsf')
        # Let's mix ascii and non-ascii strings and unicode.
        self.ff1.fsf.fgVocabulary = (
            '1|one', '2|two', '3|three', u'4|fo\xfcr', '5|f\xc3\xacve')

        # first test inside the vocabulary
        request = self.fakeRequest(fsf = '2')
        val = self.ff1['fsf'].htmlValue(request)
        self.assertEqual( val, 'two')

        # now, outside the vocabulary
        request = self.fakeRequest(fsf = '7')
        val = self.ff1['fsf'].htmlValue(request)
        self.assertEqual( val, '7')

        # now, outside the vocabulary;
        # make sure it's html escaped
        request = self.fakeRequest(fsf = '&')
        val = self.ff1['fsf'].htmlValue(request)
        self.assertEqual( val, '&amp;')

        # Now test unicode
        request = self.fakeRequest(fsf = '4')
        val = self.ff1['fsf'].htmlValue(request)
        self.assertEqual(val, u'fo\xfcr'.encode('utf-8'))

        # And test a non-ascii string
        request = self.fakeRequest(fsf = '5')
        val = self.ff1['fsf'].htmlValue(request)
        self.assertEqual(val, 'f\xc3\xacve')

    def testHtmlValueMultiSelectionField(self):
        """ Test field htmlValue method of multi-selection field """

        self.ff1.invokeFactory('FormMultiSelectionField', 'fsf')
        # Let's mix ascii and non-ascii strings and unicode.
        self.ff1.fsf.fgVocabulary = (
            '1|one', '2|two', '3|three', u'4|fo\xfcr', '5|f\xc3\xacve')

        # first test inside the vocabulary
        request = self.fakeRequest(fsf = ['2', '3', ''])
        val = self.ff1['fsf'].htmlValue(request)
        self.assertEqual( val, 'two, three')

        # now, outside the vocabulary
        request = self.fakeRequest(fsf = ['7', ''])
        val = self.ff1['fsf'].htmlValue(request)
        self.assertEqual( val, '7')

        # now, outside the vocabulary;
        # make sure it's html-escaped
        request = self.fakeRequest(fsf = ['&', ''])
        val = self.ff1['fsf'].htmlValue(request)
        self.assertEqual( val, '&amp;')

        # now, mixed
        request = self.fakeRequest(fsf = ['1', '7', ''])
        val = self.ff1['fsf'].htmlValue(request)
        self.assertEqual( val, 'one, 7')

        # Now test ascii and non-ascii strings and unicode.
        request = self.fakeRequest(fsf = ['1', '4', '5'])
        val = self.ff1['fsf'].htmlValue(request)
        self.assertEqual(val, 'one, fo\xc3\xbcr, f\xc3\xacve')
        self.assertEqual(val.decode('utf-8'), u'one, fo\xfcr, f\xecve')

    def testHtmlValueDateField(self):
        """ Test field htmlValue method of date field """

        self.ff1.invokeFactory('FormDateField', 'fdf')

        # good date
        request = self.fakeRequest(fdf = '2007/01/01 00:00')
        val = self.ff1['fdf'].htmlValue(request)

        # bad date
        request = self.fakeRequest(fdf = '2007/01/00 00:00')
        val = self.ff1['fdf'].htmlValue(request)


    def testMissingAdapter(self):
        """ test response to missing adapter -- should not fail """

        # Note: this test logs a warning message; it does not indicate test failure

        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')

        self.ff1.setActionAdapter( ('bogus',) )
        self.assertEqual(self.ff1.actionAdapter, ('bogus',))

        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )


    def testSimpleCall(self):
        """ test calling form """

        # this proves we can call a form from the test
        # harness.

        self.ff1()


    def testCallWithGoodOverride(self):
        """ test calling form with good code in override """

        # This test isn't as trivial as it looks. It makes sure the
        # call to the override doesn't clobber the expression context
        # and foul template evaluation.

        self.ff1.setOnDisplayOverride("python: 1")
        self.ff1()


    def testCallWithAfterValidationOverride(self):
        """ test calling form with good code in AfterValidationOverride """

        self.ff1.setAfterValidationOverride("python: 1")
        self.ff1()


    def testCallWithBadOverride(self):
        """ test calling form with bad code in override """

        self.ff1.setOnDisplayOverride("python: 1/0")
        self.assertRaises(ZeroDivisionError, self.ff1)


    def testCatalogCleanup(self):
        """ Test to make sure portalfactory isn't leaving
            ghost entries in portal_catalog """

        # look up all the FormStringFields
        sfb = self.portal.portal_catalog(portal_type='FormStringField')
        # There should be two
        self.assertEqual(len(sfb), 2)



    def testEmptySelectionField(self):
        """ test for issue  #80: No radio button selected: AttributeError
            'NoneType' object has no attribute 'encode' """

        self.ff1.invokeFactory('FormSelectionField', 'fsf')
        self.ff1.fsf.fgVocabulary = ('one', 'two', 'three', 'four', 'five')
        self.ff1.fsf.setFgFormat('radio')

        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org', comments='test comments')
        self.ff1.fsf.htmlValue(request)



    def testEmptyMultiSelectionField(self):
        """ check MSF for issue  #80: No radio button selected: AttributeError
            'NoneType' object has no attribute 'encode' """

        self.ff1.invokeFactory('FormMultiSelectionField', 'fsf')
        self.ff1.fsf.fgVocabulary = ('one', 'two', 'three', 'four', 'five')
        self.ff1.fsf.setFgFormat('checkbox')

        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org', comments='test comments')
        self.ff1.fsf.htmlValue(request)



    def testTrailSpacesValidation(self):
        """ check MSF for issue  #79:
            Trailing space in recipient address of mailer causes validation failure"""

        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org ', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )



    def testTrailSpacesSave(self):
        """ We really don't want to save or act on trailing spaces in inputs """

        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org ', comments='test comments')
        self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( request.form['replyto'], 'test@test.org' )



    def testWhiteSpaceInRequired(self):
        """ white-space only shouldn't validate in required fields  """

        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org', comments='\n')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( len(errors), 1 )

        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org', comments='xx\n')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( len(errors), 0 )

        request = self.fakeRequest(topic = '   ', replyto='test@test.org', comments='xx\n')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( len(errors), 1 )

        request = self.fakeRequest(topic = 'x   ', replyto='test@test.org', comments='xx\n')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( len(errors), 0 )


    def testListMarshallFix(self):
        """ test fgvalidate fix for odd Zope list marshalling """

        self.ff1.invokeFactory('FormMultiSelectionField', 'fsf')
        self.ff1.fsf.fgVocabulary = ('one', 'two', 'three', 'four', 'five')
        self.ff1.fsf.setFgFormat('checkbox')
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org', comments='test', fsf=['one','two',''])
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )
        # print request.form['fsf']
        self.assertEqual( len(request.form['fsf']), 2 )


    def testFieldEnables(self):
        """ Test TAL field enables/disables  """

        # crude test: see if fields are enabled or not by testing
        # whether or not they get validated.

        # no enabling condition: should not validate
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( len(errors), 1 )

        # explicity enabling: should not validate
        self.ff1.comments.setFgTEnabled('python: True')
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( len(errors), 1 )

        # explicity disabling: should validate
        self.ff1.comments.setFgTEnabled('python: False')
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( len(errors), 0 )

        # now, let's count fields returned by fgFields

        # no enabling condition: all fields should be in list
        self.ff1.comments.setFgTEnabled('')
        request = self.fakeRequest()
        fields = self.ff1.fgFields(request=request)
        self.assertEqual( len(fields), 3 )

        # explicitly enabled: all fields should be in list
        self.ff1.comments.setFgTEnabled('python: True')
        request = self.fakeRequest()
        fields = self.ff1.fgFields(request=request)
        self.assertEqual( len(fields), 3 )

        # explicitly disabled: one less fields should be in list
        self.ff1.comments.setFgTEnabled('python: False')
        request = self.fakeRequest()
        fields = self.ff1.fgFields(request=request)
        self.assertEqual( len(fields), 2 )


    def testTranslationBasics(self):
        """ Sanity check i18n setup against some known translations
            This test will fail if .mo files don't exist.
        """

        from Products.PloneFormGen import PloneFormGenMessageFactory as _
        from zope.i18n import translate

        # test with:
        # msgid "clear-save-input"

        msg = _(u"clear-save-input", u"Clear Saved Input")

        xlation = translate(msg, target_language='en')
        self.assertEqual( xlation, u"Clear Saved Input" )

        # xlation = translate(msg, target_language='fr')
        # self.assertEqual( xlation, 'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'.decode('utf-8') )

        # xlation = translate(msg, target_language='de')
        # self.assertEqual( xlation, 'Die gespeicherten Eingaben l\xc3\xb6schen'.decode('utf-8') )


    def testDateValidation(self):
        """ Dates should be validated """

        self.ff1.invokeFactory('FormDateField', 'fdf')
        # set non-date fields in request
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org ', comments='test comments')

        # try with no date at all. should validate, since fdf isn't required
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( request.form['replyto'], 'test@test.org' )
        self.assertEqual( errors, {} )

        # try with good date. should validate.
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org ', comments='test comments',
         fdf='2007/02/20')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( request.form['replyto'], 'test@test.org' )
        self.assertEqual( errors, {} )

        # try with bad date. should not validate.
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org ', comments='test comments',
         fdf='2007-02-31')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( request.form['replyto'], 'test@test.org' )
        self.assertEqual( len(errors), 1 )

        # try required and bad date. should not validate.
        self.ff1.fdf.setRequired(True)
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org ', comments='test comments',
         fdf='2007-02-31')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( request.form['replyto'], 'test@test.org' )
        self.assertEqual( len(errors), 1 )

        # try required and no date. should not validate.
        self.ff1.fdf.setRequired(True)
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org ', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( request.form['replyto'], 'test@test.org' )
        self.assertEqual( len(errors), 1 )

        # try required and good date. should validate.
        self.ff1.fdf.setRequired(True)
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org ', comments='test comments',
         fdf='2007-02-21')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( request.form['replyto'], 'test@test.org' )
        self.assertEqual( errors, {} )

    def testEmptyHiddenLinesField(self):
        """ test empty, hidden lines field, issue 151 """

        self.ff1.invokeFactory('FormLinesField', 'flf')
        self.ff1.flf.setHidden(True)
        # smoke test
        self.ff1()

    def testActionAdapterReturns(self):
        """ test to make sure that the return status of action adapters is handled right """

        # Script code to imitate a Custom Script adapter
        # script returning something other than a dict
        non_error_script="""
        ## Python Script
        ##bind container=container
        ##bind context=context
        ##bind subpath=traverse_subpath
        ##parameters=fields, ploneformgen, request
        ##title=Succesfully working script returning error
        ##

        return False
        """

        # Script code to imitate a Custom Script adapter
        # script returning a dict and using context.FORM_ERROR_MARKER
        error_script="""
        ## Python Script
        ##bind container=container
        ##bind context=context
        ##bind subpath=traverse_subpath
        ##parameters=fields, ploneformgen, request
        ##title=Succesfully working script returning error
        ##

        return {context.FORM_ERROR_MARKER:'an error message'}
        """

        # we'll need privileges to create a script adapter
        self.loginAsPortalOwner()

        # create three adapters
        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver1')
        saver1 = self.ff1.saver1
        self.ff1.invokeFactory('FormCustomScriptAdapter', 'cscript')
        cscript = self.ff1.cscript
        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver2')
        saver2 = self.ff1.saver2
        self.ff1.setActionAdapter( ('saver1', 'cscript', 'saver2') )
        self.assertEqual(self.ff1.actionAdapter, ('saver1', 'cscript', 'saver2'))

        # fake request to fake post
        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org', comments='test comments')

        # Run a script that returns a non-error status;
        # Something should be saved to both savers,
        # and errors should be an empty dict.
        cscript.setScriptBody(stripWhiteSpace(non_error_script))
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual(errors, {})
        self.assertEqual(saver1.itemsSaved(), 1)
        self.assertEqual(saver2.itemsSaved(), 1)

        # Run a script that returns an error status;
        # we should see an error status from the validator,
        # and action adapter execution should short-circuit
        # with only the first saver's onSuccess being executed.
        #
        # This will also demonstrate that the dictionary returned
        # by the action adapter is returned by fgvalidate
        # and that FORM_ERROR_MARKER is available as an
        # attribute of the context.
        cscript.setScriptBody(stripWhiteSpace(error_script))
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual(errors, {cscript.FORM_ERROR_MARKER : 'an error message'})
        self.assertEqual(saver1.itemsSaved(), 2)
        self.assertEqual(saver2.itemsSaved(), 1)

    def testCSRF(self):
        """ test csrf protection """

        # for this test, we need a bit more serious request simulation
        from ZPublisher.HTTPRequest import HTTPRequest
        from ZPublisher.HTTPResponse import HTTPResponse
        environ = {}
        environ.setdefault('SERVER_NAME', 'foo')
        environ.setdefault('SERVER_PORT', '80')
        environ.setdefault('REQUEST_METHOD',  'POST')
        request = HTTPRequest(sys.stdin,
                    environ,
                    HTTPResponse(stdout=sys.stdout))

        request.form = \
             {'topic':'test subject',
              'replyto':'test@test.org',
              'comments':'test comments'}

        self.ff1.checkAuthenticator = True

        self.assertRaises(zExceptions.Forbidden, self.ff1.fgvalidate, request)

        # with authenticator... no error
        tag = AuthenticatorView('context', 'request').authenticator()
        token = tag.split('"')[5]
        request.form['_authenticator'] = token
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )

        # sneaky GET request
        environ['REQUEST_METHOD'] = 'GET'
        request = HTTPRequest(sys.stdin,
                    environ,
                    HTTPResponse(stdout=sys.stdout))
        self.assertRaises(zExceptions.Forbidden, self.ff1.fgvalidate, request)

        # bad authenticator
        request.form['_authenticator'] = 'inauthentic'
        request = HTTPRequest(sys.stdin,
                    environ,
                    HTTPResponse(stdout=sys.stdout))
        self.assertRaises(zExceptions.Forbidden, self.ff1.fgvalidate, request)


    def testBooleanRequired(self):
        """ test for issue  #202: bad enforcement of required
            on boolean fields
        """

        self.ff1.invokeFactory('FormBooleanField', 'fbf')
        self.ff1.fbf.setRequired(True)

        request = self.fakeRequest(topic = 'test subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )
