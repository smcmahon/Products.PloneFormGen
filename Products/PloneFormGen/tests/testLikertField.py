#
# Likert Field related tests
#
from ZPublisher.HTTPRequest import record

from Products.PloneFormGen.tests import pfgtc


class FakeRequest(dict):

    def __init__(self, **kwargs):
        self.form = kwargs

class TestLikertField(pfgtc.PloneFormGenTestCase):
    """ tests that mostly concern the Likert Field.
        field instantiation is tested in testSetup,
        so we don't bother with it here.
    """

    def setUp(self):
        # build a form folder, add a Likert Field and
        # a saver.
        pfgtc.PloneFormGenTestCase.setUp(self)
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
        self.ff1.invokeFactory('FormLikertField', 'lf')
        self.lf = getattr(self.ff1, 'lf')
        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')
        self.saver = getattr(self.ff1, 'saver')
        self.ff1.setActionAdapter( ('saver',) )

    def test_Setup(self):
        """ Test field setup """
        lf = self.lf
        # check default question and answer set
        self.assertEqual(len(lf.likertQuestions), 2)
        self.assertEqual(len(lf.likertAnswers), 5)
        self.assertEqual(len(lf.fgField.questionSet), 2)
        self.assertEqual(len(lf.fgField.answerSet), 5)


    def test_Validate(self):
        """ Test required field validation """

        # try it with no input, unrequired
        request = FakeRequest(topic = 'test subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )
        self.assertEqual(self.saver.itemsSaved(), 1)
        self.assertEqual(self.saver.getSavedFormInput()[0][3], '')

        # try it with no input, required
        self.lf.setRequired(True)
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {'lf': u'pfg_allRequired'} )

        # try it with input, required
        request = FakeRequest(topic = 'test subject',
                              replyto='test@test.org',
                              comments='test comments',
                              lf={'1':'2','2':'3'})
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )
        self.assertEqual(self.saver.itemsSaved(), 2)
        self.assertEqual(self.saver.getSavedFormInput()[1][3], "{'1': '2', '2': '3'}")

    def test_likert_html_output(self):
        """Failing test for #225, AttributeError: __len__" in Plone 2.5.5"""
        rating_req_val = record()
        rating_req_val.__dict__ = {'1':'2','2':'3'}
        request = FakeRequest(topic = 'test subject', replyto='test@test.org',
                              comments='test comments', lf=rating_req_val)
        self.failUnless("1: 2, 2: 3" in self.ff1.lf.htmlValue(request))
