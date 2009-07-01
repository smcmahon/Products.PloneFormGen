import sys, traceback
import DateTime
import simplejson as json
from pprint import pprint

from zope import component
from zope import httpform
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

def processSaveData(rawinp):
    """Process raw input and return as dictionary value
    """
    env = {'REQUEST_METHOD': 'GET', 'QUERY_STRING': rawinp}
    try:
        return parse(env)
    except:
        print rawinp
        raise

class FormBuildView(BrowserView):
    """View use for add/save/load field
    """

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.form = context
        self.action = request.form.get('action','')
        self.postdata = json.loads(request.form.get('data',''))
        self._response = {'status': 'success', 
                          'message': None, #{'type':'info', 'content':'xxx'}, 
                          'data': None
                          }
        self.portal = getToolByName(context,'portal_url').getPortalObject()

    def setStatus(self, status, message=None):
        self._response['status'] = status
        self._response['message'] = message

    def setResponse(self, data):
        self._response['data'] = data

    def doAdd(self):
        """Action = adding new field
        """

    def doSort(self):
        """Action = sorting field
        """

    def doSave(self):
        """Action = save form settings
        """

    def doDelete(self):
        """Action = delete field
        """

    def __call__(self):
        actions = {
                    'add'   : self.doAdd,
                    'save'  : self.doSave,
                    'delete': self.doDelete,
                    'sort'  : self.doSort
                  }
        action = actions.get(self.action, None)
        if action is not None:
            action()
        else:
            self.setStatus('failure', 'Unrecognize action: %s' %action)

        return json.dumps(self._response)


