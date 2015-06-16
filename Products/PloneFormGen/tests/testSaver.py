# Integration tests specific to save-data adapter.
#
import sys
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
import zExceptions

from Products.PloneFormGen.tests import pfgtc

from Products.CMFCore.utils import getToolByName
import plone.protect

# dummy class
class cd:
    pass

def FakeRequest(method="GET", add_auth=False, **kwargs):
    environ = {}
    environ.setdefault('SERVER_NAME', 'foo')
    environ.setdefault('SERVER_PORT', '80')
    environ.setdefault('REQUEST_METHOD', method)
    request = HTTPRequest(sys.stdin,
                environ,
                HTTPResponse(stdout=sys.stdout))
    request.form = kwargs
    if add_auth:
        request.form['_authenticator'] = plone.protect.createToken()
    return request


class TestFunctions(pfgtc.PloneFormGenTestCase):
    """ test save data adapter """

    def setUp(self):
        pfgtc.PloneFormGenTestCase.setUp(self)
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')

    def testSaver(self):
        """ test save data adapter action """

        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')

        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver

        self.ff1.setActionAdapter( ('saver',) )
        self.assertEqual(self.ff1.actionAdapter, ('saver',))

        # print "|%s|" % saver.SavedFormInput
        self.assertEqual(saver.itemsSaved(), 0)

        res = saver.getSavedFormInputForEdit()
        self.assertEqual(res, '')

        request = FakeRequest(add_auth=True, method='POST', topic = 'test subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )

        self.assertEqual(saver.itemsSaved(), 1)

        res = saver.getSavedFormInputForEdit()
        self.assertEqual(res.strip(), 'test@test.org,test subject,test comments')


    def testSaverSavedFormInput(self):
        """ test save data adapter action and direct access to SavedFormInput """

        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')

        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver

        self.ff1.setActionAdapter( ('saver',) )

        request = FakeRequest(add_auth=True, method='POST', topic = 'test subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )

        self.assertEqual(saver.itemsSaved(), 1)
        row = iter(saver.getSavedFormInput()).next()
        self.assertEqual(len(row), 3)

        request = FakeRequest(add_auth=True, method='POST', topic = 'test subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )
        self.assertEqual(saver.itemsSaved(), 2)

        self.ff1.saver._clearSavedFormInput()
        self.assertEqual(saver.itemsSaved(), 0)


    def testSetSavedFormInput(self):
        """ test setSavedFormInput functionality """

        # set up saver
        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')
        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver

        # save a row
        saver.setSavedFormInput('one,two,three')
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(saver._inputStorage[0], ['one', 'two', 'three'])

        # save a couple of \n-delimited rows - \n eol
        saver.setSavedFormInput('one,two,three\nfour,five,six')
        self.assertEqual(saver.itemsSaved(), 2)
        self.assertEqual(saver._inputStorage[0], ['one', 'two', 'three'])
        self.assertEqual(saver._inputStorage[1], ['four', 'five', 'six'])

        # save a couple of \n-delimited rows -- \r\n eol
        saver.setSavedFormInput('one,two,three\r\nfour,five,six')
        self.assertEqual(saver.itemsSaved(), 2)

        # save a couple of \n-delimited rows -- \n\n double eol
        saver.setSavedFormInput('one,two,three\n\nfour,five,six')
        self.assertEqual(saver.itemsSaved(), 2)

        # save empty string
        saver.setSavedFormInput('')
        self.assertEqual(saver.itemsSaved(), 0)

        # save empty list
        saver.setSavedFormInput(tuple())
        self.assertEqual(saver.itemsSaved(), 0)

    def testSetSavedFormInputAlternateDelimiter(self):
        """ test setSavedFormInput functionality when an alternate csv delimiter
            has been specified
        """
        # set prefered delimiter
        pft = getToolByName(self.portal, 'formgen_tool')
        alt_delimiter = '|'
        pft.setDefault('csv_delimiter', alt_delimiter)
        # set up saver
        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')
        saver = self.ff1.saver

        # build and save a row
        row1 = alt_delimiter.join(('one','two','three'))
        saver.setSavedFormInput(row1)
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(saver._inputStorage[0], ['one', 'two', 'three'])

        # save a couple of \n-delimited rows - \n eol
        row2 = alt_delimiter.join(('four','five','six'))
        saver.setSavedFormInput('%s\n%s' % (row1, row2))
        self.assertEqual(saver.itemsSaved(), 2)
        self.assertEqual(saver._inputStorage[0], ['one', 'two', 'three'])
        self.assertEqual(saver._inputStorage[1], ['four', 'five', 'six'])

        # save a couple of \n-delimited rows -- \r\n eol
        saver.setSavedFormInput('%s\r\n%s' % (row1, row2))
        self.assertEqual(saver.itemsSaved(), 2)

        # save a couple of \n-delimited rows -- \n\n double eol
        saver.setSavedFormInput('%s\n\n%s' % (row1, row2))
        self.assertEqual(saver.itemsSaved(), 2)

        # save empty string
        saver.setSavedFormInput('')
        self.assertEqual(saver.itemsSaved(), 0)

        # save empty list
        saver.setSavedFormInput(tuple())
        self.assertEqual(saver.itemsSaved(), 0)


    def testEditSavedFormInput(self):
        """ test manage_saveData functionality """

        # set up saver
        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')
        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver

        # save a row
        saver.setSavedFormInput('one,two,three')
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(saver._inputStorage.values()[0], ['one', 'two', 'three'])

        data = cd()
        setattr(data, 'item-0', 'four')
        setattr(data, 'item-1', 'five')
        setattr(data, 'item-2', 'six')

        # We should need an authenticator
        self.assertRaises(zExceptions.Forbidden, saver.manage_saveData, *[saver._inputStorage.keys()[0], data])

        saver.REQUEST = FakeRequest(add_auth=True, method="POST")
        saver.manage_saveData(saver._inputStorage.keys()[0], data)

        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(saver._inputStorage.values()[0], ['four', 'five', 'six'])

    def testEditSavedFormInputWithAlternateDelimiter(self):
        """ test manage_saveData functionality when an alternate csv delimiter is used """

        # set prefered delimiter
        pft = getToolByName(self.portal, 'formgen_tool')
        alt_delimiter = '|'
        pft.setDefault('csv_delimiter', alt_delimiter)

        # set up saver
        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')
        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver

        # save a row
        saver.setSavedFormInput('one|two|three')
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(saver._inputStorage.values()[0], ['one', 'two', 'three'])

        data = cd()
        setattr(data, 'item-0', 'four')
        setattr(data, 'item-1', 'five')
        setattr(data, 'item-2', 'six')

        saver.REQUEST = FakeRequest(add_auth=True, method="POST")
        saver.manage_saveData(saver._inputStorage.keys()[0], data)
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(saver._inputStorage.values()[0], ['four', 'five', 'six'])

    def testRetrieveDataSavedBeforeSwitchingDelimiter(self):
        """ test manage_saveData functionality when an alternate csv delimiter is used """

        # set up saver
        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')
        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver

        # save a row
        saver.setSavedFormInput('one,two,three')
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(saver._inputStorage.values()[0], ['one', 'two', 'three'])

        # switch prefered delimiter
        pft = getToolByName(self.portal, 'formgen_tool')
        alt_delimiter = '|'
        pft.setDefault('csv_delimiter', alt_delimiter)

        # verify we can retrieve based on new delimiter
        self.assertEqual(saver.itemsSaved(), 1)
        self.assertEqual(saver._inputStorage.values()[0], ['one', 'two', 'three'])

    def testDeleteSavedFormInput(self):
        """ test manage_deleteData functionality """

        # set up saver
        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')
        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver

        # save a few rows
        saver._addDataRow( ['one','two','three'] )
        saver._addDataRow( ['four','five','six'] )
        saver._addDataRow( ['seven','eight','nine'] )
        self.assertEqual(saver.itemsSaved(), 3)

        saver.manage_deleteData(saver._inputStorage.keys()[1])
        self.assertEqual(saver.itemsSaved(), 2)
        self.assertEqual(saver._inputStorage.values()[0], ['one', 'two', 'three'])
        self.assertEqual(saver._inputStorage.values()[1], ['seven', 'eight', 'nine'])


    def testSaverInputAsDictionaries(self):
        """ test save data adapter's InputAsDictionaries """

        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')

        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver

        self.ff1.setActionAdapter( ('saver',) )

        self.assertEqual(saver.inputAsDictionaries, saver.InputAsDictionaries)

        self.assertEqual(saver.itemsSaved(), 0)

        request = FakeRequest(add_auth=True, method='POST', topic = 'test subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )

        self.assertEqual(saver.itemsSaved(), 1)

        iad = saver.InputAsDictionaries()
        row = iter(iad).next()
        self.assertEqual(len(row), 3)
        self.assertEqual(row['topic'], 'test subject')



    def testSaverColumnNames(self):
        """ test save data adapter's getColumnNames function """

        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')

        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver

        self.ff1.setActionAdapter( ('saver',) )

        cn = saver.getColumnNames()
        self.failUnless( len(cn) == 3 )
        self.failUnless( cn[0] == 'replyto')
        self.failUnless( cn[1] == 'topic')
        self.failUnless( cn[2] == 'comments')

        # Use selective field saving
        saver.setShowFields(('topic', 'comments'))
        cn = saver.getColumnNames()
        self.failUnless( len(cn) == 2 )
        self.failUnless( cn[0] == 'topic')
        self.failUnless( cn[1] == 'comments')
        saver.setShowFields(())

        # Add an extra column
        saver.ExtraData = ('dt',)
        cn = saver.getColumnNames()
        self.failUnless( len(cn) == 4 )
        self.failUnless( cn[3] == 'dt' )

        # add a label field -- should not show up in column names
        self.ff1.invokeFactory('FormLabelField', 'alabel')
        cn = saver.getColumnNames()
        self.failUnless( len(cn) == 4 )

        # add a form field -- should show up in column names before 'dt'
        self.ff1.invokeFactory('FormFileField', 'afile')
        cn = saver.getColumnNames()
        self.failUnless( len(cn) == 5 )
        self.failUnless( cn[3] == 'afile')
        self.failUnless( cn[4] == 'dt')


    def testSaverColumnTitles(self):
        """ test save data adapter's getColumnTitles function """

        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')

        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver

        self.ff1.setActionAdapter( ('saver',) )

        cn = saver.getColumnTitles()
        self.failUnless( len(cn) == 3 )
        self.failUnless( cn[0] == 'Your E-Mail Address')
        self.failUnless( cn[1] == 'Subject')
        self.failUnless( cn[2] == 'Comments')

        # Add an extra column
        saver.ExtraData = ('dt',)
        cn = saver.getColumnTitles()
        self.failUnless( len(cn) == 4 )
        self.failUnless( cn[3] == 'Posting Date/Time' )


    def testSaverSelectiveFieldSaving(self):
        """ Test selective inclusion of fields in the data"""

        self.ff1.invokeFactory('FormSaveDataAdapter', 'saver')

        self.failUnless('saver' in self.ff1.objectIds())
        saver = self.ff1.saver
        saver.setShowFields(('topic', 'comments'))

        self.ff1.setActionAdapter( ('saver',) )

        request = FakeRequest(add_auth=True, method='POST', topic='test subject', replyto='test@test.org', comments='test comments')
        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )

        self.assertEqual(saver.itemsSaved(), 1)
        row = iter(saver.getSavedFormInput()).next()
        self.assertEqual(len(row), 2)
        self.assertEqual(row[0], 'test subject')
        self.assertEqual(row[1], 'test comments')

    # the csrf test has moved to browser.txt
