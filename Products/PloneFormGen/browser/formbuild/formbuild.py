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
            newfield = self.fieldfactory.addField(fieldtype, pos, 
                                                  {
                                                   "title" : "New %s" %fieldtype
                                                  })
        except:
            traceback.print_exc()
            print 'Got %s: %s' %(sys.exc_type, sys.exc_value)
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': '%s: %s' %(sys.exc_type, sys.exc_value)
                           })
            return
        #TODO: Do restrictedTraverse save ? 
        newfield = getattr(self.context, newfield)
        renderer = newfield.restrictedTraverse('fieldrenderer')
        self.setResponse({'fieldid':newfield.getId(), 'html':renderer()})

    def doMove(self):
        """Action = sorting fields
        """
        fieldid = self.postdata.get('fieldid', '')
        pos = self.postdata.get('position', -1);
        if pos < 0 :
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Invalid new position'
                           })
            return
        try:
            self.fieldfactory.moveField(fieldid, pos)
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
        poststr = self.postdata.get('poststr')
        data = processSaveData(poststr)
        errors = self.fieldfactory.saveField(fieldid, data)
        if errors:
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Please correct the following errors'
                           })
        else:
            self.setStatus('success',
                           {'type':'info',
                            'content':'Field saved'
                           })

        #Generate return's html
        field = getattr(self.context, fieldid)
        renderer = field.restrictedTraverse('fieldrenderer')
        #TODO: Since I don't know how to make a request programatically
        #      I created the field then set the errors attribute
        #      We should find a more elegant way to implement 
        renderer.errors = errors
        self.setResponse({'html':renderer()})

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

    def doCopy(self):
        """Action = clone a existed field
        """
        fieldid = self.postdata.get('fieldid', '')
        try:
            newfield = self.fieldfactory.copyField(fieldid)
        except:
            traceback.print_exc()
            print 'Got %s: %s' %(sys.exc_type, sys.exc_value)
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': '%s: %s' %(sys.exc_type, sys.exc_value)
                           })
            return
        #TODO: Do restrictedTraverse save ? 
        newfield = getattr(self.context, newfield)
        renderer = newfield.restrictedTraverse('fieldrenderer')
        self.setResponse({'fieldid':newfield.getId(), 'html':renderer()})

    def __call__(self):
        actions = {
                    'add'   : self.doAdd,
                    'save'  : self.doSave,
                    'delete': self.doDelete,
                    'move'  : self.doMove,
                    'copy'  : self.doCopy
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


