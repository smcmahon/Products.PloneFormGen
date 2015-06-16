from Products.PloneFormGen.tests import pfgtc

import transaction
from ZPublisher.Publish import Retry

class FakeRequest(dict):

    def __init__(self, **kwargs):
        self.form = kwargs

class TrueOnceCalled(object):
    """ A mock function that evaluates to True once it has been called. """
    def __init__(self):
        self.called = False
    def __call__(self, *args, **kw):
        self.called = True
    def __bool__(self):
        return self.called

class TestEmbedding(pfgtc.PloneFormGenTestCase):
    """ test embedding of a PFG in another template """

    def dummy_send( self, mfrom, mto, messageText, immediate=False ):
        self.mfrom = mfrom
        self.mto = mto
        self.messageText = messageText

    def LoadRequestForm(self, **kwargs):
        form = self.app.REQUEST.form
        form.clear()
        for key in kwargs.keys():
            form[key] = kwargs[key]
        return self.app.REQUEST

    def setUp(self):
        pfgtc.PloneFormGenTestCase.setUp(self)
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        self.ff1.checkAuthenticator = False # no csrf protection
        self.mailhost = self.folder.MailHost
        self.mailhost._send = self.dummy_send
        self.ff1.mailer.setRecipient_email('mdummy@address.com')

    def test_embedded_form_renders(self):
        view = self.ff1.restrictedTraverse('@@embedded')
        res = view()

        # form renders
        self.failUnless('Your E-Mail Address' in res)

        # form action equals request URL
        self.failUnless('action="%s"' % self.app.REQUEST['URL'] in res)

        # no form prefix
        self.failUnless('name="form.submitted"' in res)

        # we can specify a form prefix
        view.setPrefix('mypfg')
        res = view()
        self.failUnless('name="mypfg.form.submitted"' in res)

    def test_embedded_form_validates(self):
        # fake an incomplete form submission
        self.LoadRequestForm(**{
            'mypfg.form.submitted': True,
            })

        # render the form
        view = self.ff1.restrictedTraverse('@@embedded')
        view.setPrefix('mypfg')
        res = view()

        # should stay on same page on errors, and show messages
        self.failUnless('This field is required.' in res)

    def test_doesnt_process_submission_of_other_form(self):
        # fake submission of a *different* form (note mismatch of form submission marker with prefix)
        self.LoadRequestForm(**{
            'form.submitted': True,
            })

        # let's preset a faux controller_state (as if from the other form)
        # to make sure it doesn't throw things off
        self.app.REQUEST.set('controller_state', 'foobar')

        # render the form
        view = self.ff1.restrictedTraverse('@@embedded')
        view.setPrefix('mypfg')
        res = view()

        # should be no validation errors
        self.failIf('This field is required.' in res)

        # (and request should still have the 'form.submitted' key)
        self.failUnless('form.submitted' in self.app.REQUEST.form)

        # (and the controller state should be untouched)
        self.assertEqual(self.app.REQUEST.get('controller_state'), 'foobar')

        # but if we remove the form prefix then it should process the form
        view.setPrefix('')
        res = view()
        self.failUnless('This field is required.' in res)

    def test_render_thank_you_on_success(self):
        # We need to be able to make sure the transaction commit was called
        # before the Retry exception, without actually committing our test
        # fixtures.
        real_transaction_commit = transaction.commit
        transaction.commit = committed = TrueOnceCalled()

        self.LoadRequestForm(**{
            'form.submitted': True,
            'topic': 'monkeys',
            'comments': 'I am not a walnut.',
            'replyto': 'foobar@example.com'
            })
        # should raise a retry exception triggering a new publish attempt
        # with the new URL
        # XXX do a full publish for this test
        self.app.REQUEST._orig_env['PATH_TRANSLATED'] = '/plone'
        view = self.ff1.restrictedTraverse('@@embedded')
        self.assertRaises(Retry, view)

        self.assertEqual(self.app.REQUEST._orig_env['PATH_INFO'],
            '/'.join(self.folder.getPhysicalPath()) + '/ff1/thank-you/@@embedded')

        # make sure the transaction was committed
        self.failUnless(committed)

        # make sure it can deal with VHM URLs
        self.app.REQUEST._orig_env['PATH_TRANSLATED'] = '/VirtualHostBase/http/nohost:80/VirtualHostRoot'
        self.assertRaises(Retry, view)
        self.assertEqual(self.app.REQUEST._orig_env['PATH_INFO'],
            '/VirtualHostBase/http/nohost:80/VirtualHostRoot' +
            '/'.join(self.folder.getPhysicalPath()) +
            '/ff1/thank-you/@@embedded')

        # clean up
        transaction.commit = real_transaction_commit
