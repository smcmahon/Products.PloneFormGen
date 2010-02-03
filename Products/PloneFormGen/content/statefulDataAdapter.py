""" A form action adapter that saves form submissions within a data
structure for later retrieval by the form - i.e. retains state """

__author__  = 'Ben Ackland <ben@netsight.co.uk>'
__docformat__ = 'plaintext'

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from persistent.dict import PersistentDict

from Products.ATContentTypes.content.base import registerATCT
from Products.CMFPlone.utils import base_hasattr, safe_hasattr
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.PloneFormGen.config import *
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter
from Products.PloneFormGen.interfaces import IPloneFormGenPersistentActionAdapter
import logging
import time
import re
from csv import writer
from StringIO import StringIO
from DateTime import DateTime


logger = logging.getLogger("PloneFormGen")    

COOKIENAME = 'pfg_statefuldata_uniqueid'
LARGE_DATA_SET_LENGTH = 7

class FormStatefulDataAdapter(FormActionAdapter):
    implements(IPloneFormGenPersistentActionAdapter)

    meta_type      = 'FormStatefulDataAdapter'
    portal_type    = 'FormStatefulDataAdapter'
    archetype_name = 'Stateful Data Adapter'

    immediate_view = 'fg_statefuldata_view'
    default_view   = 'fg_statefuldata_view'
    suppl_views    = ()
    
    security       = ClassSecurityInfo()

    def __init__(self, REQUEST):
        self.statefuldata = PersistentDict()
        super(FormStatefulDataAdapter, self).__init__(REQUEST)

    def onSuccess(self, fields, REQUEST=None, loopstop=False):
        """
        saves data in a stateful manner.
        """
        logger.info("FormStatefulDataAdapter: onSuccess")
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
                if target.meta_type == 'FormStatefulDataAdapter':
                    target.onSuccess(fields, REQUEST, loopstop=True)
                    return
        
        final_data = {}
        for f in fields:
            if f.isFileField():
                # TODO - deal with file fields
                pass
            elif not f.isLabel():
                fname_id = f.fgField.getName()
                val = REQUEST.form.get(fname_id,None)
                title = f.title
                final_data[fname_id] = dict(field_value = val, title = title, field_type = f.portal_type)

        # add in the date this was submitted
        final_data['submission_date'] = dict(field_value = DateTime().strftime('%c'),
                                             title = 'Submission Date',
                                             field_type = 'FormStringField')

        # If the user has selected to fill this form in as another user
        # use this as the key, if not, use they key in the REQUEST
        if self.REQUEST.form.get('user-select'):
            key = self.REQUEST.form['user-select']
        else:
            key = self.getKey(REQUEST)
        
        # Check to see if this is a single submission form or a multi submission form
        if self.aq_parent.getPersistentActionAdapter():
            # This is a single submission form so overwrite the data
            self.statefuldata[key] = [final_data]
        else:            
            # This is a multi submission form
            new_data = self.statefuldata[key][:]
            new_data.append(final_data)
            self.statefuldata[key] = new_data

    def itemsSaved(self):
        """Download the saved data"""
        return len(self.statefuldata)

    security.declareProtected(ModifyPortalContent, 'getStatefulData')
    def getStatefulData(self):
        """ Return the current data """
        result = dict(self.statefuldata.copy())
        user_keys = result.keys()

        # check if we have a multi submission or single
        # XXX we should no longer get passed dicts
        if type(result[user_keys[0]]) == dict:
            # each user should have a list containing one or more dicts
            for user in user_keys:
                result[user] = [result[user]]

        # create a new data structure
        sane_data = {}
        for user in user_keys:
            for index, data in enumerate(result[user]):
                new_key = user + '-' + str(index)
                member = self.portal_membership.getMemberById(user)
                data['user'] = dict(user_key = user, 
                                    field_value = self.getFullName(member, user),
                                    title = 'User',
                                    field_type = 'FormStringField'
                                    )
                sane_data[new_key] = data                
        return sane_data

    security.declareProtected(ModifyPortalContent, 'resetStatefulData')
    def resetStatefulData(self):
        """ reset all my data """
        self.statefuldata = PersistentDict()
        return "Reset Stateful Data OK"

    def isLargeStatefulDataSet(self):
        """ check if the data set is larger than 8 columns """
        data = self.formFolderObject().fgFields(displayOnly=True)
        if len(data) > LARGE_DATA_SET_LENGTH:
            return True

    def saveStatefulDataCSV(self):
        """ Save the data out as a csv """
        data = self.getStatefulData()

        title = re.sub('\s+', '', self.title)
        csv_file_name = title + '.csv'

        output = StringIO()
        csv_writer = writer(output)

        #The first column should always be the user
        first_row = ['User']
        main_keys = data.keys()
        # Write out header row
        if main_keys: 
            ids = data[main_keys[0]].keys()
            for id in ids:
                first_row.append(id)
            csv_writer.writerow(first_row)

        for key in data:
            write_list = []
            write_list.append(key)
            content_keys = data[key].keys()
            for content_key in content_keys:
                # If we have a list, insert them as a colon seperated string
                if type(data[key][content_key]['field_value']) == list:
                    csv_list_content = ' : '.join(data[key][content_key]['field_value'])
                    write_list.append(csv_list_content)
                else:
                    write_list.append(data[key][content_key]['field_value'])
            csv_writer.writerow(write_list)

        self.REQUEST.RESPONSE.setHeader("Content-type", "text/csv")
        self.REQUEST.RESPONSE.setHeader("Content-Disposition", 
                                           "attachment;filename=%s" % csv_file_name)

        value = output.getvalue() 
        output.close()
        return value

    def getKey(self, REQUEST):
        """ get key based on logged-in user or cookie/session """
        portal_membership = getToolByName(self, 'portal_membership')
        isAnon = portal_membership.isAnonymousUser()
        member = portal_membership.getAuthenticatedMember()
        if REQUEST.form.get('override_key') and 'Manager' in member.getRolesInContext(self):
            return REQUEST.form.get('override_key')
        if not isAnon:
            return member.getId()

        # See if we have a uniqueid
        if REQUEST.has_key(COOKIENAME):
            return REQUEST.get(COOKIENAME)
        # If not, create a cookie
        uniqueid = str(time.time())
        REQUEST.set(COOKIENAME, uniqueid)
        REQUEST.RESPONSE.setCookie(COOKIENAME, uniqueid, expires='Wed, 19 Feb 2020 14:28:00 GMT')
        return uniqueid

    def getCurrentFieldValue(self, field, REQUEST):
        """ get the value for the field from the statefuldata """
        key = self.getKey(REQUEST)
        if key in self.statefuldata.keys():
            # get the most recent submission
            last_submission = len(self.statefuldata[key]) - 1
            data = self.statefuldata[key][last_submission]
            if field.id in data.keys():
                return data[field.id]['field_value']
        return None

    def getStatefulFieldValue(self, data, user_id, field_id):
        """ get the correct value for the stateful adapter view """        
        if type(data[user_id]) == dict:
            if data[user_id].has_key(field_id):
                return data[user_id][field_id]['field_value']
            else:
                return ''
        else:
            if data[user_id][0].has_key(field_id):
                return data[user_id][0][field_id]['field_value']
            else:
                return ''

    def currentUserHasCompletedForm(self, REQUEST):
        key = self.getKey(REQUEST)
        if key in self.statefuldata.keys():
            return True
        return False

    def resetCurrentUserPersistentData(self, REQUEST):
        key = self.getKey(REQUEST)
        if key in self.statefuldata.keys():
            del(self.statefuldata[key])

    def getFullName(self, user, userid):
        """ try to get the fullname of the user """
        try:
            fullname = user.getProperty('fullname', userid)
        except AttributeError:
            fullname = 'No user'
        return fullname

    def statefulFormAdapterSummary(self, data):
        """ return statistics for select and checkbox fields """        
        users = data.keys()
        field_types = ['FormSelectionField', 'FormMultiSelectionField']

        data_oc = []
        data_types = []        
        
        for user in users:
            if type(data[user]) == dict:
                user_data = data[user]
            else:
                user_data = data[user][0]
            for key in user_data:
                d_value = user_data[key]['field_value']
                if user_data[key]['field_type'] in field_types:
                    if type(d_value) is list and len(d_value) == 1:
                        f_value = user_data[key]['field_value'][0]
                    else:
                        f_value = user_data[key]['field_value']
                    data_oc.append(f_value)
                    if f_value not in data_types:
                        data_types.append(f_value)

        final_counts = {}
        for data_type in data_types:
            count = data_oc.count(data_type)
            data_type = str(data_type)
            final_counts[data_type] = count
                    
        return final_counts

registerATCT(FormStatefulDataAdapter, PROJECTNAME)
