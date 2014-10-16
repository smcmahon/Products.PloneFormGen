""" A form action adapter that saves form submissions for download """

__author__ = 'Steve McMahon <steve@dcn.org>'
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo

from BTrees.IOBTree import IOBTree
try:
    from BTrees.LOBTree import LOBTree
    SavedDataBTree = LOBTree
except ImportError:
    SavedDataBTree = IOBTree
from BTrees.Length import Length

from zope.contenttype import guess_content_type

import plone.protect

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.utils import base_hasattr, safe_hasattr

from Products.Archetypes.public import *
from Products.Archetypes.utils import contentDispositionHeader
from Products.ATContentTypes.content.base import registerATCT

from Products.PloneFormGen import PloneFormGenMessageFactory as _
from Products.PloneFormGen.config import *
from Products.PloneFormGen.content.actionAdapter import \
    FormActionAdapter, FormAdapterSchema

import logging
import time

from DateTime import DateTime
import csv
from StringIO import StringIO
from types import StringTypes

logger = logging.getLogger("PloneFormGen")

ExLinesField = LinesField


class FormSaveDataAdapter(FormActionAdapter):
    """A form action adapter that will save form input data and
       return it in csv- or tab-delimited format."""

    schema = FormAdapterSchema.copy() + Schema((
        LinesField('showFields',
            required=0,
            searchable=0,
            vocabulary='allFieldDisplayList',
            widget=PicklistWidget(
                label=_(u'label_savefields_text', default=u"Saved Fields"),
                description=_(u'help_savefields_text', default=u"""
                    Pick the fields whose inputs you'd like to include in
                    the saved data. If empty, all fields will be saved.
                    """),
                ),
            ),
        LinesField('ExtraData',
            widget=MultiSelectionWidget(
                label=_(u'label_savedataextra_text', default='Extra Data'),
                description=_(u'help_savedataextra_text', default=u"""
                    Pick any extra data you'd like saved with the form input.
                    """),
                format='checkbox',
                ),
            vocabulary='vocabExtraDataDL',
            ),
        StringField('DownloadFormat',
            searchable=0,
            required=1,
            default='csv',
            vocabulary='vocabFormatDL',
            widget=SelectionWidget(
                label=_(u'label_downloadformat_text', default=u'Download Format'),
                ),
            ),
        BooleanField("UseColumnNames",
            required=False,
            searchable=False,
            widget=BooleanWidget(
                label=_(u'label_usecolumnnames_text', default=u"Include Column Names"),
                description=_(u'help_usecolumnnames_text', default=u"Do you wish to have column names on the first line of downloaded input?"),
                ),
            ),
        ExLinesField('SavedFormInput',
            edit_accessor='getSavedFormInputForEdit',
            mutator='setSavedFormInput',
            searchable=0,
            required=0,
            primary=1,
            schemata="saved data",
            read_permission=DOWNLOAD_SAVED_PERMISSION,
            widget=TextAreaWidget(
                label=_(u'label_savedatainput_text', default=u"Saved Form Input"),
                description=_(u'help_savedatainput_text'),
                ),
            ),
    ))

    schema.moveField('execCondition', pos='bottom')

    meta_type      = 'FormSaveDataAdapter'
    portal_type    = 'FormSaveDataAdapter'
    archetype_name = 'Save Data Adapter'

    immediate_view = 'fg_savedata_view_p3'
    default_view   = 'fg_savedata_view_p3'
    suppl_views    = ('fg_savedata_tabview_p3', 'fg_savedata_recview_p3',)

    security       = ClassSecurityInfo()


    def _migrateStorage(self):
        # we're going to use an LOBTree for storage. we need to
        # consider the possibility that self is from an
        # older version that uses the native Archetypes storage
        # or the former IOBTree (<= 1.6.0b2 )
        # in the SavedFormInput field.
        updated = base_hasattr(self, '_inputStorage') and \
                  base_hasattr(self, '_inputItems') and \
                  base_hasattr(self, '_length')

        if not updated:
            try:
                saved_input = self.getSavedFormInput()
            except AttributeError:
                saved_input = []

            self._inputStorage = SavedDataBTree()
            i = 0
            self._inputItems = 0
            self._length = Length()

            if len(saved_input):
                for row in saved_input:
                    self._inputStorage[i] = row
                    i += 1
                self.SavedFormInput = []
                self._inputItems = i
                self._length.set(i)


    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'getSavedFormInput')
    def getSavedFormInput(self):
        """ returns saved input as an iterable;
            each row is a sequence of fields.
        """

        if base_hasattr(self, '_inputStorage'):
            return self._inputStorage.values()
        else:
            return self.SavedFormInput


    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'getSavedFormInputItems')
    def getSavedFormInputItems(self):
        """ returns saved input as an iterable;
            each row is an (id, sequence of fields) tuple
        """
        if base_hasattr(self, '_inputStorage'):
            return self._inputStorage.items()
        else:
            return enumerate(self.SavedFormInput)


    security.declareProtected(ModifyPortalContent, 'getSavedFormInputForEdit')
    def getSavedFormInputForEdit(self, **kwargs):
        """ returns saved as CSV text """
        delimiter = self.csvDelimiter()
        sbuf = StringIO()
        writer = csv.writer(sbuf, delimiter=delimiter)
        for row in self.getSavedFormInput():
            writer.writerow(row)
        res = sbuf.getvalue()
        sbuf.close()

        return res


    security.declareProtected(ModifyPortalContent, 'setSavedFormInput')
    def setSavedFormInput(self, value, **kwargs):
        """ expects value as csv text string, stores as list of lists """

        self._migrateStorage()

        self._inputStorage.clear()
        i = 0
        self._inputItems = 0
        self._length.set(0)

        if len(value):
            delimiter = self.csvDelimiter()
            sbuf = StringIO(value)
            reader = csv.reader(sbuf, delimiter=delimiter)
            for row in reader:
                if row:
                    self._inputStorage[i] = row
                    i += 1
                self._inputItems = i
                self._length.set(i)
            sbuf.close()

        # logger.debug("setSavedFormInput: %s items" % self._inputItems)

    def _clearSavedFormInput(self):
        # convenience method to clear input buffer

        self._migrateStorage()

        self._inputStorage.clear()
        self._inputItems = 0
        self._length.set(0)

    security.declareProtected(ModifyPortalContent, 'clearSavedFormInput')
    def clearSavedFormInput(self, **kwargs):
        """ clear input buffer TTW """

        plone.protect.CheckAuthenticator(self.REQUEST)
        plone.protect.PostOnly(self.REQUEST)
        self._clearSavedFormInput()
        self.REQUEST.response.redirect(self.absolute_url())

    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'getSavedFormInputById')
    def getSavedFormInputById(self, id):
        """ Return the data stored for record with 'id' """
        lst = [field.replace('\r', '').replace('\n', r'\n') for field in self._inputStorage[id]]
        return lst

    security.declareProtected(ModifyPortalContent, 'manage_saveData')
    def manage_saveData(self, id,  data):
        """ Save the data for record with 'id' """

        plone.protect.CheckAuthenticator(self.REQUEST)
        plone.protect.PostOnly(self.REQUEST)

        self._migrateStorage()

        lst = list()
        for i in range(0, len(self.getColumnNames())):
            lst.append(getattr(data, 'item-%d' % i, '').replace(r'\n', '\n'))

        self._inputStorage[id] = lst
        self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/view')


    security.declareProtected(ModifyPortalContent, 'manage_deleteData')
    def manage_deleteData(self, id):
        """ Delete the data for record with 'id' """

        self._migrateStorage()

        del self._inputStorage[id]
        self._inputItems -= 1
        self._length.change(-1)

        self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/view')


    def _addDataRow(self, value):

        self._migrateStorage()

        if isinstance(self._inputStorage, IOBTree):
            # 32-bit IOBTree; use a key which is more likely to conflict
            # but which won't overflow the key's bits
            id = self._inputItems
            self._inputItems += 1
        else:
            # 64-bit LOBTree
            id = int(time.time() * 1000)
            while id in self._inputStorage:  # avoid collisions during testing
                id += 1
        self._inputStorage[id] = value
        self._length.change(1)


    security.declareProtected(ModifyPortalContent, 'addDataRow')
    def addDataRow(self, value):
        # """ a wrapper for the _addDataRow method """

        self._addDataRow(value)


    security.declarePrivate('onSuccess')
    def onSuccess(self, fields, REQUEST=None, loopstop=False):
        # """
        # saves data.
        # """

        if LP_SAVE_TO_CANONICAL and not loopstop:
            # LinguaPlone functionality:
            # check to see if we're in a translated
            # form folder, but not the canonical version.
            parent = self.aq_parent
            if safe_hasattr(parent, 'isTranslation') and \
               parent.isTranslation() and not parent.isCanonical():
                # look in the canonical version to see if there is
                # a matching (by id) save-data adapter.
                # If so, call its onSuccess method
                cf = parent.getCanonical()
                target = cf.get(self.getId())
                if target is not None and target.meta_type == 'FormSaveDataAdapter':
                    target.onSuccess(fields, REQUEST, loopstop=True)
                    return

        from ZPublisher.HTTPRequest import FileUpload

        data = []
        for f in fields:
            showFields = getattr(self, 'showFields', [])
            if showFields and f.id not in showFields:
                continue
            if f.isFileField():
                file = REQUEST.form.get('%s_file' % f.fgField.getName())
                if isinstance(file, FileUpload) and file.filename != '':
                    file.seek(0)
                    fdata = file.read()
                    filename = file.filename
                    mimetype, enc = guess_content_type(filename, fdata, None)
                    if mimetype.find('text/') >= 0:
                        # convert to native eols
                        fdata = fdata.replace('\x0d\x0a', '\n').replace('\x0a', '\n').replace('\x0d', '\n')
                        data.append('%s:%s:%s:%s' % (filename, mimetype, enc, fdata))
                    else:
                        data.append('%s:%s:%s:Binary upload discarded' %  (filename, mimetype, enc))
                else:
                    data.append('NO UPLOAD')
            elif not f.isLabel():
                val = REQUEST.form.get(f.fgField.getName(), '')
                if not type(val) in StringTypes:
                    # Zope has marshalled the field into
                    # something other than a string
                    val = str(val)
                data.append(val)

        if self.ExtraData:
            for f in self.ExtraData:
                if f == 'dt':
                    data.append(str(DateTime()))
                else:
                    data.append(getattr(REQUEST, f, ''))


        self._addDataRow(data)


    security.declareProtected(ModifyPortalContent, 'allFieldDisplayList')
    def allFieldDisplayList(self):
        # """ returns a DisplayList of all fields """
        return self.fgFieldsDisplayList()


    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'getColumnNames')
    def getColumnNames(self, excludeServerSide=True):
        # """Returns a list of column names"""

        showFields = getattr(self, 'showFields', [])
        names = [field.getName() for field
                 in self.fgFields(displayOnly=True, excludeServerSide=excludeServerSide)
                 if not showFields or field.getName() in showFields]
        for f in self.ExtraData:
            names.append(f)

        return names


    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'getColumnTitles')
    def getColumnTitles(self, excludeServerSide=True):
        # """Returns a list of column titles"""

        names = [field.widget.label for field
                 in self.fgFields(displayOnly=True, excludeServerSide=excludeServerSide)]
        for f in self.ExtraData:
            names.append(self.vocabExtraDataDL().getValue(f, ''))

        return names


    def _cleanInputForTSV(self, value):
        # make data safe to store in tab-delimited format

        return  str(value).replace('\x0d\x0a', r'\n').replace('\x0a', r'\n').replace('\x0d', r'\n').replace('\t', r'\t')


    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'download_tsv')
    def download_tsv(self, REQUEST=None, RESPONSE=None):
        # """Download the saved data
        # """

        filename = self.id
        if filename.find('.') < 0:
            filename = '%s.tsv' % filename
        header_value = contentDispositionHeader('attachment', self.getCharset(), filename=filename)
        RESPONSE.setHeader("Content-Disposition", header_value)
        RESPONSE.setHeader("Content-Type", 'text/tab-separated-values;charset=%s' % self.getCharset())

        if getattr(self, 'UseColumnNames', False):
            res = "%s\n" % '\t'.join(self.getColumnNames(excludeServerSide=False))
            if isinstance(res, unicode):
                res = res.encode(self.getCharset())
        else:
            res = ''

        for row in self.getSavedFormInput():
            res = '%s%s\n' % (res, '\t'.join([self._cleanInputForTSV(col) for col in row]))

        return res


    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'download_csv')
    def download_csv(self, REQUEST=None, RESPONSE=None):
        # """Download the saved data
        # """

        filename = self.id
        if filename.find('.') < 0:
            filename = '%s.csv' % filename
        header_value = contentDispositionHeader('attachment', self.getCharset(), filename=filename)
        RESPONSE.setHeader("Content-Disposition", header_value)
        RESPONSE.setHeader("Content-Type", 'text/comma-separated-values;charset=%s' % self.getCharset())

        if getattr(self, 'UseColumnNames', False):
            delimiter = self.csvDelimiter()
            res = "%s\n" % delimiter.join(self.getColumnNames(excludeServerSide=False))
            if isinstance(res, unicode):
                res = res.encode(self.getCharset())
        else:
            res = ''

        return '%s%s' % (res, self.getSavedFormInputForEdit())


    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """Download the saved data
        """

        format = getattr(self, 'DownloadFormat', 'tsv')
        if format == 'tsv':
            return self.download_tsv(REQUEST, RESPONSE)
        else:
            assert format == 'csv', 'Unknown download format'
            return self.download_csv(REQUEST, RESPONSE)


    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'rowAsColDict')
    def rowAsColDict(self, row, cols):
        # """ Where row is a data sequence and cols is a column name sequence,
        #     returns a dict of colname:column. This is a convenience method
        #     used in the record view.
        # """

        colcount = len(cols)

        rdict = {}
        for i in range(0, len(row)):
            if i < colcount:
                rdict[cols[i]] = row[i]
            else:
                rdict['column-%s' % i] = row[i]
        return rdict


    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'inputAsDictionaries')
    def inputAsDictionaries(self):
        # """returns saved data as an iterable of dictionaries
        # """

        cols = self.getColumnNames()

        for row in self.getSavedFormInput():
            yield self.rowAsColDict(row, cols)


    # alias for old mis-naming
    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'InputAsDictionaries')
    InputAsDictionaries = inputAsDictionaries


    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'formatMIME')
    def formatMIME(self):
        # """MIME format selected for download
        # """

        format = getattr(self, 'DownloadFormat', 'tsv')
        if format == 'tsv':
            return 'text/tab-separated-values'
        else:
            assert format == 'csv', 'Unknown download format'
            return 'text/comma-separated-values'

    security.declarePrivate('csvDelimiter')
    def csvDelimiter(self):
        # """Delimiter character for CSV downloads
        # """
        fgt = getToolByName(self, 'formgen_tool')
        return fgt.getCSVDelimiter()

    security.declareProtected(DOWNLOAD_SAVED_PERMISSION, 'itemsSaved')
    def itemsSaved(self):
        # """Download the saved data
        # """

        if base_hasattr(self, '_length'):
            return self._length()
        elif base_hasattr(self, '_inputItems'):
            return self._inputItems
        else:
            return len(self.SavedFormInput)

    def vocabExtraDataDL(self):
        # """ returns vocabulary for extra data """

        return DisplayList((
                ('dt',
                    self.translate(msgid='vocabulary_postingdt_text',
                    domain='ploneformgen',
                    default='Posting Date/Time')
                    ),
                ('HTTP_X_FORWARDED_FOR', 'HTTP_X_FORWARDED_FOR',),
                ('REMOTE_ADDR', 'REMOTE_ADDR',),
                ('HTTP_USER_AGENT', 'HTTP_USER_AGENT',),
                ))


    def vocabFormatDL(self):
        # """ returns vocabulary for format """

        return DisplayList((
                ('tsv',
                    self.translate(msgid='vocabulary_tsv_text',
                    domain='ploneformgen',
                    default='Tab-Separated Values')
                    ),
                ('csv',
                    self.translate(msgid='vocabulary_csv_text',
                    domain='ploneformgen',
                    default='Comma-Separated Values')
                    ),
            ))



registerATCT(FormSaveDataAdapter, PROJECTNAME)
