"""Tests for the Submission Folder adapter."""

__author__  = 'Ross Patterson <me@rpatterson.net>'
__docformat__ = 'plaintext'

from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_base
from Testing import makerequest

from Products.CMFCore.utils import getToolByName

from Products.Archetypes import public

from Products.PloneFormGen.tests import pfgtc


class TestCustomScript(pfgtc.PloneFormGenTestCase):
    """Tests for the Submission Folder adapter."""

    def afterSetUp(self):
        """Create a form folder with a submission folder adapter."""
        pfgtc.PloneFormGenTestCase.afterSetUp(self)

        self.loginAsPortalOwner()
        makerequest.makerequest(self.app)

        self.folder.invokeFactory(
            'FormFolder', 'foo-form-folder', title='Foo Form Folder')
        self.form = self.folder['foo-form-folder']
        self.form.checkAuthenticator = False
        self.form.manage_delObjects(['replyto', 'comments', 'mailer'])
        self.form.invokeFactory(
            'FormSubmissionFolderAdapter',
            'foo-submissions', title='Foo Submissions')
        self.adapter = self.form['foo-submissions']

        self.app.REQUEST.form['topic'] = 'Foo Submission Topic'
        
    def test_form_schema_field_methods(self):
        """
        Form submission schemata are extended with fields that generate methods
        """
        self.form.fgvalidate(self.app.REQUEST)
        self.assertIn(
            'foo-submission-topic', self.form['foo-submissions'],
            'Form submission not found in the submission folder')
        submission = self.form['foo-submissions']['foo-submission-topic']
        schema = submission.Schema()
        self.assertIn(
            'title', schema, 'Form field missing from submission schema')
        field = schema['title']

        accessor = field.getAccessor(submission)
        self.assertEqual(
            accessor(), self.app.REQUEST.form['topic'],
            'Wrong submission accessor value')

        mutator = field.getMutator(submission)
        mutator('Bar Submission Topic')
        self.assertEqual(
            submission.title, 'Bar Submission Topic',
            'Wrong submission mutated value')
        
    def test_saves_submissions(self):
        """
        The Submission Folder adapter saves submissions.
        """
        self.form.fgvalidate(self.app.REQUEST)

        self.assertIn(
            'foo-submission-topic', self.form['foo-submissions'],
            'Form submission not found in the submission folder')
        submission = self.form['foo-submissions']['foo-submission-topic']
        self.assertEqual(
            submission.portal_type,
            self.form['foo-submissions'].getSubmissionType(),
            'Wrong form submission type')

        self.logout()
        self.assertFalse(
            getSecurityManager().checkPermission('View', submission),
            'New form submission is publicly visible')
        self.loginAsPortalOwner()
        
        self.assertIn(
            'title', submission.Schema(),
            'Form field missing from submission schema')
        foo_field_value = submission.Schema()['title'].get(submission)
        self.assertEqual(
            foo_field_value, self.app.REQUEST.form['topic'],
            'Wrong submission field value')

        # add another submission with the same title and id
        self.form.fgvalidate(self.app.REQUEST)
        self.assertIn(
            'foo-submission-topic-1', self.form['foo-submissions'],
            'Duplicate form submission not found in the submission folder')
        self.form.fgvalidate(self.app.REQUEST)
        self.assertIn(
            'foo-submission-topic-2', self.form['foo-submissions'],
            'Duplicate submission not found in the submission folder')
        
    def test_anonymous_saves_submissions(self):
        """
        The Submission Folder adapter saves submissions from anonymous users.
        """
        workflow = getToolByName(self.form, 'portal_workflow')
        workflow.doActionFor(self.form, 'publish')
        self.logout()

        self.assertNotIn(
            'foo-submission-topic', self.form['foo-submissions'],
            'Form submission not found in the submission folder')
        self.form.fgvalidate(self.app.REQUEST)
        self.assertIn(
            'foo-submission-topic', self.form['foo-submissions'],
            'Form submission not found in the submission folder')
        submission = self.form['foo-submissions']['foo-submission-topic']
        self.assertEqual(
            submission.getOwnerTuple(), self.adapter.getOwnerTuple(),
            'Wrong anonymous submission owner')
        self.assertFalse(
            getSecurityManager().checkPermission('View', submission),
            'Anonymous form submission is publicly visible')
        
    def test_other_user_saves_submissions(self):
        """
        The Submission Folder adapter saves submissions from other users.
        """
        workflow = getToolByName(self.form, 'portal_workflow')
        workflow.doActionFor(self.form, 'publish')

        membership = getToolByName(self.form, 'portal_membership')
        membership.addMember('foo-user', 'secret', ('Member', ), ())
        self.login('foo-user')

        self.assertNotIn(
            'foo-submission-topic', self.form['foo-submissions'],
            'Form submission not found in the submission folder')
        self.form.fgvalidate(self.app.REQUEST)
        self.assertIn(
            'foo-submission-topic', self.form['foo-submissions'],
            'Form submission not found in the submission folder')
        submission = self.form['foo-submissions']['foo-submission-topic']
        self.assertEqual(
            submission.getOwnerTuple(),
            (list(self.portal.acl_users.getPhysicalPath()[1:]), 'foo-user'),
            'Wrong other member submission owner')

    def test_submission_title_field(self):
        """
        The adapter supports specifying the submission title field.
        """
        self.form.invokeFactory(
            'FormStringField', 'foo-field', title='Foo Field')
        self.adapter.update(titleField='foo-field')

        self.app.REQUEST.form['foo-field'] = 'foo field value'
        self.form.fgvalidate(self.app.REQUEST)

        self.assertIn(
            'foo-field-value', self.form['foo-submissions'],
            'Custom title field submission not found in the submission folder')
        self.assertNotIn(
            'foo-submission-topic', self.form['foo-submissions'],
            'Wrong submission title found in the submission folder')
        submission = self.form['foo-submissions']['foo-field-value']

        self.assertEqual(
            submission.title, 'foo field value',
            'Wrong submission field value')
        self.assertEqual(
            submission.topic, 'Foo Submission Topic',
            'Wrong submission field value')
        self.assertFalse(
            hasattr(aq_base(submission), 'foo-field'),
            'Wrong submission attribute')

    def test_submission_type_and_folder_field(self):
        """
        The adapter supports specifying the submission type.
        """
        self.adapter.update(
            submissionType='Event', submissionFolder=self.portal.events)

        self.form.fgvalidate(self.app.REQUEST)

        self.assertIn(
            'foo-submission-topic', self.portal.events,
            'Custom title field submission not found in the submission folder')
        submission = self.portal.events['foo-submission-topic']
        self.assertEqual(
            submission.portal_type, 'Event', 'Wrong form submission type')

    def test_submission_transitions_field(self):
        """
        Support specifying workflow transistions to apply to the submission.
        """
        self.adapter.update(submissionTransitions=['submit', 'publish'])

        self.form.fgvalidate(self.app.REQUEST)

        self.assertIn(
            'foo-submission-topic', self.form['foo-submissions'],
            'Custom title field submission not found in the submission folder')
        submission = self.form['foo-submissions']['foo-submission-topic']

        self.logout()
        self.assertTrue(
            getSecurityManager().checkPermission('View', submission),
            'New form submission is not publicly visible')
        self.loginAsPortalOwner()

    def test_adapter_vocabs(self):
        """
        The vocabularies work for each of the adapter fields.
        """
        for field in self.adapter.Schema().fields():
            if not isinstance(field.widget, (
                    public.SelectionWidget, public.MultiSelectionWidget,
                    public.PicklistWidget)):
                # Vocab not used
                continue
            vocab = field.Vocabulary(self.adapter)
            self.assertIsInstance(
                vocab, public.DisplayList, 'Wrong field vocabulary type')
            self.assertTrue(len(vocab), 'Wrong field vocabulary type')

    def test_submission_folder_vocab(self):
        """
        The submission folder vocabulary includes the right types.
        """
        vocab, enforce = self.adapter.Vocabulary('submissionFolder')
        self.assertIsNotNone(
            vocab.getKey('News'), 'Missing submission folder')
        self.assertIsInstance(
            vocab.getKey('News'), str, 'Wrong submission folder UID type')
        self.assertIsNotNone(
            vocab.getKey(self.adapter.Title()),
            'Missing adapter in folderish types')
        self.assertIsNone(
            vocab.getKey(self.portal['front-page'].Title()),
            'Non-folderish item included in submission folder vocab')

    def test_form_submission_types_vocab(self):
        """
        The form submission type vocabulary includes the right types.
        """
        vocab, enforce = self.adapter.Vocabulary('submissionType')
        self.assertIsNotNone(
            vocab.getValue('Document'), 'Missing submission type')
        self.assertEqual(
            vocab.getValue('Document'),
            'Page', 'Wrong submission type title')
        self.assertIsNone(
            vocab.getValue('FormSubmissionFolderAdapter'),
            'Un-addable submission type included')

    def test_transitions_vocab(self):
        """
        The workflow transition vocabulary includes the right transitions.
        """
        vocab, enforce = self.adapter.Vocabulary('submissionTransitions')
        self.assertIsNotNone(
            vocab.getValue('submit'), 'Missing workflow transition')
        self.assertEqual(
            vocab.getValue('submit'),
            'Submit for publication',
            'Wrong workflow transition title')
        self.assertIsNone(
            vocab.getValue('private'),
            'Transition included that should not be')


def test_suite():
    from unittest import TestSuite, makeSuite
    from Products.PloneTestCase.layer import ZCMLLayer
    suite = TestSuite()
    suite.layer = ZCMLLayer
    suite.addTest(makeSuite(TestCustomScript))
    return suite
