import sys, traceback
import DateTime
import simplejson as json
from pprint import pprint

from zope import component
from zope import httpform

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from Products.PloneFormGen.adapters.interfaces import IFieldFactory
from Products.PloneFormGen.interfaces import IPloneFormGenForm, \
                                    IPloneFormGenField, IPloneFormGenFieldset

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

    def getRealPos(self, pos):
        #Since the pos that we get from the client is the position of the field 
        #compare to JUST other field only, we need to get the real pos 
        if pos == 0: 
            return 0
        filters = {"object_provides": {"query":[IPloneFormGenField.__identifier__, IPloneFormGenFieldset.__identifier__], "operator": "or"}}
        fields = self.context.getFolderContents(filters)
        return fields[pos].getObject().getObjPositionInParent()

    def setStatus(self, status, message=None):
        self._response['status'] = status
        self._response['message'] = message

    def setResponse(self, data):
        self._response['data'] = data

    def doAdd(self):
        """Action = adding new field
        """
        containerpath = self.postdata.get('containerpath', '')
        fieldtype = self.postdata.get('fieldtype', '')
        pos = self.postdata.get('position', -1);
        if containerpath == "" and pos != -1:
            pos = self.getRealPos(pos)
        if not fieldtype:
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Field type is not specified'
                           })
            return 
        try:
            fieldpath = self.fieldfactory.addField(fieldtype, containerpath, pos, 
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
        newfield = self.context.restrictedTraverse(fieldpath.replace(':','/'))
        renderer = newfield.restrictedTraverse('fieldrenderer')
        self.setResponse({'fieldpath': fieldpath, 
                          'html': renderer(),
                          'js': list(renderer.helperjs()),
                          'css': list(renderer.helpercss())
                        })

    def doMove(self):
        """Action = sorting fields
        """
        fieldpath = self.postdata.get('fieldpath', '')
        containerpath = self.postdata.get('containerpath', '')
        pos = self.postdata.get('position', -1)
        if pos < 0 :
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Invalid new position'
                           })
            return
        if containerpath == "":
            pos = self.getRealPos(pos)
        try:
            self.fieldfactory.moveField(fieldpath, containerpath, pos)
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
        fieldpath = self.postdata.get('fieldpath','')
        poststr = self.postdata.get('poststr')
        data = processSaveData(poststr)
        errors = self.fieldfactory.saveField(fieldpath, data)
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
        field = self.context.restrictedTraverse(fieldpath.replace(':','/'))
        renderer = field.restrictedTraverse('fieldrenderer')
        #TODO: Since I don't know how to make a request programatically
        #      I created the field then set the errors attribute
        #      We should find a more elegant way to implement 
        renderer.errors = errors
        self.setResponse({'html':renderer()})

    def doDelete(self):
        """Action = delete field
        """
        fieldpath = self.postdata.get('fieldpath', '')
        if not fieldpath:
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': 'Field not found.'
                           })
            return 
        try:
            self.fieldfactory.deleteField(fieldpath)
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
        fieldpath = self.postdata.get('fieldpath', '')
        try:
            newfield = self.fieldfactory.copyField(fieldpath)
        except:
            traceback.print_exc()
            print 'Got %s: %s' %(sys.exc_type, sys.exc_value)
            self.setStatus('failure', 
                           {'type':'error', 
                            'content': '%s: %s' %(sys.exc_type, sys.exc_value)
                           })
            return
        newfield = getattr(self.context, newfield)
        renderer = newfield.restrictedTraverse('fieldrenderer')
        self.setStatus('success', {'type':'info', 'content':'Field copied'})
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


