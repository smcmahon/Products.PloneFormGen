# coding=utf-8
#
# Integeration tests specific to the mailer
#
import email

from Products.PloneFormGen.tests import pfgtc


class TestFunctions(pfgtc.PloneFormGenTestCase):
    """ test ya_gpg.py """

    def dummy_send( self, mfrom, mto, messageText, immediate=False ):
        self.mfrom = mfrom
        self.mto = mto
        self.messageText = messageText
        self.messageBody = '\n\n'.join(messageText.split('\n\n')[1:])

    def setUp(self):
        pfgtc.PloneFormGenTestCase.setUp(self)
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        self.ff1.checkAuthenticator = False # no csrf protection
        self.mailhost = self.folder.MailHost
        self.mailhost._send = self.dummy_send
        self.ff1.mailer.setRecipient_name('Mail Dummy')
        self.ff1.mailer.setRecipient_email('mdummy@address.com')


    def LoadRequestForm(self, **kwargs):
        form = self.app.REQUEST.form
        form.clear()
        for key in kwargs.keys():
            form[key] = kwargs[key]
        return self.app.REQUEST


    def test_DummyMailer(self):
        """ sanity check; make sure dummy mailer works as expected """

        self.mailhost.send('messageText', mto='dummy@address.com', mfrom='dummy1@address.com')
        self.failUnless( self.messageText.endswith('messageText') )
        self.assertEqual(self.mto, ['dummy@address.com'])
        self.failUnless( self.messageText.find('To: dummy@address.com') > 0 )
        self.assertEqual(self.mfrom, 'dummy1@address.com')
        self.failUnless( self.messageText.find('From: dummy1@address.com') > 0 )
        # print "|%s" % self.messageText


    def test_Mailer(self):
        """ Test mailer with dummy_send """

        mailer = self.ff1.mailer

        fields = self.ff1._getFieldObjects()

        request = self.LoadRequestForm(topic = 'test subject', comments='test comments')

        mailer.onSuccess(fields, request)

        self.failUnless( self.messageText.find('To: Mail Dummy <mdummy@address.com>') > 0 )
        self.failUnless( self.messageText.find('Subject: =?utf-8?q?test_subject?=') > 0 )
        msg = email.message_from_string(self.messageText)
        self.failUnless( msg.get_payload(decode=True).find('test comments') > 0 )


    def test_MailerLongSubject(self):
        """ Test mailer with subject line > 76 chars (Tracker #84) """

        long_subject = "Now is the time for all good persons to come to the aid of the quick brown fox."

        mailer = self.ff1.mailer
        fields = self.ff1._getFieldObjects()
        request = self.LoadRequestForm(topic = long_subject)
        mailer.onSuccess(fields, request)

        msg = email.message_from_string(self.messageText)
        encoded_subject_header = msg['subject']
        decoded_header = email.Header.decode_header(encoded_subject_header)[0][0]

        self.assertEqual( decoded_header, long_subject )


    def test_SubjectDollarReplacement(self):
        """
        Simple subject lines should do ${identifier} replacement from request.form --
        but only for a basic override.
        """

        mailer = self.ff1.mailer
        mailer.msg_subject = 'This is my ${topic} now'

        # baseline unchanged
        request = self.LoadRequestForm(topic = 'test subject', replyto='test@test.org', comments='test comments')
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless( self.messageText.find('Subject: =?utf-8?q?test_subject?=') > 0 )

        # no substitution on field replacement (default situation)
        request = self.LoadRequestForm(topic = 'test ${subject}', replyto='test@test.org', comments='test comments')
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless( self.messageText.find('Subject: =?utf-8?q?test_=24=7Bsubject=7D?=') > 0 )

        # we should get substitution in a basic override
        mailer.subject_field = ''
        request = self.LoadRequestForm(topic = 'test subject', replyto='test@test.org', comments='test comments')
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless( self.messageText.find('Subject: =?utf-8?q?This_is_my_test_subject_now?=') > 0 )

        # we should get substitution in a basic override
        mailer.msg_subject = 'This is my ${untopic} now'
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless( self.messageText.find('Subject: =?utf-8?q?This_is_my_=3F=3F=3F_now?=') > 0 )

        # we don't want substitution on user input
        request = self.LoadRequestForm(topic = 'test ${subject}', replyto='test@test.org', comments='test comments')
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless( self.messageText.find('Subject: =?utf-8?q?This_is_my_=3F=3F=3F_now?=') > 0 )


    def test_TemplateReplacement(self):
        """
        Mail template prologues, epilogues and footers should do ${identifier}
        replacement from request.form -- this is simpler because there are no
        overrides.
        """

        mailer = self.ff1.mailer
        mailer.body_pre = 'Hello ${topic},'
        mailer.body_post = 'Thanks, ${topic}!'
        mailer.body_footer = 'Eat my footer, ${topic}.'

        # we should get substitution
        request = self.LoadRequestForm(topic = 'test subject', replyto='test@test.org', comments='test comments')
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless( self.messageBody.find('Hello test subject,') > 0 )
        self.failUnless( self.messageBody.find('Thanks, test subject!') > 0 )
        self.failUnless( self.messageBody.find('Eat my footer, test subject.') > 0 )


    def test_utf8Subject(self):
        """ Test mailer with uft-8 encoded subject line """

        utf8_subject = 'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'

        mailer = self.ff1.mailer
        fields = self.ff1._getFieldObjects()
        request = self.LoadRequestForm(topic = utf8_subject)
        mailer.onSuccess(fields, request)

        msg = email.message_from_string(self.messageText)
        encoded_subject_header = msg['subject']
        decoded_header = email.Header.decode_header(encoded_subject_header)[0][0]

        self.assertEqual( decoded_header, utf8_subject )


    def test_UnicodeSubject(self):
        """ Test mailer with Unicode encoded subject line """

        utf8_subject = 'Effacer les entr\xc3\xa9es sauvegard\xc3\xa9es'
        unicode_subject= utf8_subject.decode('utf-8')

        mailer = self.ff1.mailer
        fields = self.ff1._getFieldObjects()
        request = self.LoadRequestForm(topic = unicode_subject)
        mailer.onSuccess(fields, request)

        msg = email.message_from_string(self.messageText)
        encoded_subject_header = msg['subject']
        decoded_header = email.Header.decode_header(encoded_subject_header)[0][0]

        self.assertEqual( decoded_header, utf8_subject )


    def test_MailerOverrides(self):
        """ Test mailer override functions """

        mailer = self.ff1.mailer
        mailer.setSubjectOverride("python: '%s and %s' % ('eggs', 'spam')")
        mailer.setSenderOverride("string: spam@eggs.com")
        mailer.setRecipientOverride("string: eggs@spam.com")

        fields = self.ff1._getFieldObjects()

        request = self.LoadRequestForm(topic = 'test subject')

        mailer.onSuccess(fields, request)

        # print "|%s" % self.messageText
        self.failUnless( self.messageText.find('Subject: =?utf-8?q?eggs_and_spam?=') > 0 )
        self.failUnless( self.messageText.find('From: spam@eggs.com') > 0 )
        self.failUnless( self.messageText.find('To: Mail Dummy <eggs@spam.com>') > 0 )


    def testMultiRecipientOverrideByString(self):
        """ try multiple recipients in recipient override """

        mailer = self.ff1.mailer
        mailer.setRecipientOverride("string: eggs@spam.com, spam@spam.com")

        fields = self.ff1._getFieldObjects()

        request = self.LoadRequestForm(topic = 'test subject')

        mailer.onSuccess(fields, request)

        self.failUnless( self.messageText.find('To: Mail Dummy <eggs@spam.com>, <spam@spam.com>') > 0 )



    def testMultiRecipientOverrideByTuple(self):
        """ try multiple recipients in recipient override """

        mailer = self.ff1.mailer
        mailer.setRecipientOverride("python: ('eggs@spam.com', 'spam.spam.com')")

        fields = self.ff1._getFieldObjects()

        request = self.LoadRequestForm(topic = 'test subject')

        mailer.onSuccess(fields, request)

        # print "|%s" % self.messageText
        self.failUnless( self.messageText.find('To: Mail Dummy <eggs@spam.com>, <spam.spam.com>') > 0 )



    def testRecipientFromRequest(self):
        """ try recipient from designated field  """

        mailer = self.ff1.mailer
        mailer.setTo_field("selField")

        fields = self.ff1._getFieldObjects()

        request = self.LoadRequestForm(topic = 'test subject', selField = 'eggs@spamandeggs.com')

        mailer.onSuccess(fields, request)

        # print "|%s" % self.messageText
        self.failUnless( self.messageText.find('To: Mail Dummy <eggs@spamandeggs.com>') > 0 )

        request = self.LoadRequestForm(topic = 'test subject', selField = ['eggs@spam.com', 'spam@spam.com'])

        mailer.onSuccess(fields, request)

        # print "|%s" % self.messageText
        self.failUnless( self.messageText.find('To: Mail Dummy <eggs@spam.com>, <spam@spam.com>') > 0 )




    def test_ExecConditions(self):
        """ Test mailer with various exec conditions """

        # if an action adapter's execCondition is filled in and evaluates false,
        # the action adapter should not fire.

        mailer = self.ff1.mailer
        request = self.LoadRequestForm(topic = 'test subject', replyto='test@test.org', comments='test comments')

        self.messageText = ''
        mailer.setExecCondition('python: False')
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless( len(self.messageText) == 0 )

        self.messageText = ''
        mailer.setExecCondition('python: True')
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless( len(self.messageText) > 0 )

        self.messageText = ''
        mailer.setExecCondition('python: 1==0')
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless( len(self.messageText) == 0 )

        # make sure an empty execCondition causes the action to fire
        self.messageText = ''
        mailer.setExecCondition('')
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless( len(self.messageText) > 0 )


    def test_selectiveFieldMailing(self):
        """ Test selective inclusion of fields in the mailing """

        mailer = self.ff1.mailer
        request = self.LoadRequestForm(topic = 'test subject', replyto='test@test.org', comments='test comments')

        # make sure all fields are sent unless otherwise specified
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless(
            self.messageBody.find('test subject') > 0 and
            self.messageBody.find('test@test.org') > 0 and
            self.messageBody.find('test comments') > 0
          )

        # setting some show fields shouldn't change that
        mailer.setShowFields( ('topic', 'comments',) )
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless(
            self.messageBody.find('test subject') > 0 and
            self.messageBody.find('test@test.org') > 0 and
            self.messageBody.find('test comments') > 0
          )

        # until we turn off the showAll flag
        mailer.showAll = False
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless(
            self.messageBody.find('test subject') > 0 and
            self.messageBody.find('test@test.org') < 0 and
            self.messageBody.find('test comments') > 0
          )

        # check includeEmpties
        mailer.includeEmpties = False

        # first see if everything's still included
        mailer.showAll = True
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        # look for labels
        self.failUnless(
            self.messageBody.find('Subject') > 0 and
            self.messageBody.find('Your E-Mail Address') > 0 and
            self.messageBody.find('Comments') > 0
          )

        # now, turn off required for a field and leave it empty
        self.ff1.comments.setRequired(False)
        request = self.LoadRequestForm(topic = 'test subject', replyto='test@test.org',)
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless(
            self.messageBody.find('Subject') > 0 and
            self.messageBody.find('Your E-Mail Address') > 0 and
            self.messageBody.find('Comments') < 0
          )


    def test_bccOverride(self):
        """ Test override for BCC field """

        mailer = self.ff1.mailer
        request = self.LoadRequestForm(topic = 'test subject', replyto='test@test.org', comments='test comments')

        # simple override
        mailer.setBccOverride("string:test@testme.com")
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless(
            'test@testme.com' in self.mto
        )

        # list override
        mailer.setBccOverride( "python:['test@testme.com', 'test1@testme.com']" )
        self.messageText = ''
        self.assertEqual( self.ff1.fgvalidate(REQUEST=request), {} )
        self.failUnless(
            'test@testme.com' in self.mto and
            'test1@testme.com' in self.mto
        )
