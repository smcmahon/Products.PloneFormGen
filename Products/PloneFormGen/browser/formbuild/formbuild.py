import sys, traceback
import DateTime
import simplejson as json
from pprint import pprint

from zope import component
from zope import httpform

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from Products.PloneFormGen.adapters.interfaces import IFieldFactory

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
        self.fieldfactory = IFieldFactory(self.context)

    def setStatus(self, status, message=None):
        self._response['status'] = status
        self._response['message'] = message

    def setResponse(self, data):
        self._response['data'] = data

    def doAdd(self):
        """Action = adding new field
        """
        #TODO: We don't have "real" postdata yet :p
        fieldtype = self.postdata.get('fieldtype', '')
        pos = self.postdata.get('position', -1);
        if not fieldtype:
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Field type is not specified'
                           })
            return 
        try:
            newfield = self.fieldfactory.addField(fieldtype, position = pos)
        except:
            traceback.print_exc()
            print 'Got %s: %s' %(sys.exc_type, sys.exc_value)
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': '%s: %s' %(sys.exc_type, sys.exc_value)
                           })
            return
        #TODO: Return data that client uses to render new field + its edit form
        self.setResponse({})

    def doSort(self):
        """Action = sorting fields
        """
        #TODO: We don't have "real" postdata yet :p
        #TODO: Currently import in the way that we have many field that pos at one time
        #      Do we really need to do so ?
        orderedlist = self.postdata.get('fieldorder', None);
        if not orderedlist:
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Fields\' order is not specified'
                           })
            return
        try:
            for (pos, fieldid) in enumerate(orderedlist):
                self.fieldFactory.sortField(fieldid, pos)
        except:
            traceback.print_exc()
            print 'Got %s: %s' %(sys.exc_type, sys.exc_value)
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': '%s: %s' %(sys.exc_type, sys.exc_value)
                           })
            return

    def doSave(self):
        """Action = save form settings
        """
        #TODO: We don't have "real" postdata yet :p
        #TODO: Currently import in the way that we have many field that pos at one time
        #      Do we really need to do so ?
        data = {}
        data['settings'] = processSaveData(self.postdata['settings'])
        data['fields'] = []
        for field in self.postdata['fields']:
            data['fields'].append(processSaveData(field))
        
        state = self.form_manager.saveForm(self.form, data)
        self.setStatus(state['status'], state['error'])

    def doDelete(self):
        """Action = delete field
        """
        fieldid = self.postdata.get('fieldid', '')
        if not fieldid:
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Fields\' order is not specified'
                           })
            return 
        try:
            self.fieldfactory.deleteField(fieldid)
        except:
            traceback.print_exc()
            print 'Got %s: %s' %(sys.exc_type, sys.exc_value)
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': '%s: %s' %(sys.exc_type, sys.exc_value)
                           })
            return

    def doReload(self,):
        """Action = reload a field's html
        """
        fieldid = self.postdata.get('fieldid', '')
        errors = self.postdata.get('errors', '')
        
        self.setResponse()

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
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Unrecognize action: "%s"' %action
                           })

        return json.dumps(self._response)


