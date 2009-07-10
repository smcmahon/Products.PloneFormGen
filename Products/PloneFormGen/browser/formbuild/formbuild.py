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
        return httpform.parse(env)
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
        #TODO: Can we use current request ? 
        #      If not, then how to create a 'blank' request ?
        request = self.request
        renderer = getMultiAdapter((getattr(self.context,newfield), request), \
                                   name = 'fieldrenderer')
        self.setResponse({'fieldid':newfield, 'html':renderer()})

    def doSort(self):
        """Action = sorting fields
        """
        #TODO: Currently implement in the way that we have a new sorted list of 
        #      fieldids as agrument. But do we really need to do so ?
        orderedlist = self.postdata.get('fieldorder', None);
        if not orderedlist:
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Fields\' order is not specified'
                           })
            return
        try:
            for (pos, fieldid) in enumerate(orderedlist):
                self.fieldFactory.moveField(fieldid, pos)
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
        fieldid = self.postdata.get('fieldid', '')
        data = self.postdata.get('settings')
        errors = self.fieldfactory.saveForm(fieldid, data)
        if errors:
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Please correct the following errors'
                           })
        self.setStatus('success',
                       {'type':'info',
                        'content':'Field saved'
                       })

    def doDelete(self):
        """Action = delete field
        """
        fieldid = self.postdata.get('fieldid', '')
        if not fieldid:
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Field not found'
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
        self.setStatus('success',
                       {'type':'info',
                        'content':'Field deleted'
                       })

    #def doReload(self,):
    #    """Action = reload a field's html
    #    """
    #    fieldid = self.postdata.get('fieldid', '')
    #    errors = self.postdata.get('errors', '')
    #    self.setResponse()

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


