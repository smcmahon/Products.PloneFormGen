""" 
    
    Execute custom Python script/external method for data
    
    Copyright 2006 Red Innovation http://www.redinnovation.com
    
"""

__author__  = 'Mikko Ohtamaa <mikko@redinnovation.com>'
__docformat__ = 'plaintext'

# Python imorts
from StringIO import StringIO
import logging

# Zope imports
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from Products.PythonScripts.PythonScript import PythonScript


# Plone imports
from Products.Archetypes.public import *
from Products.Archetypes.utils import contentDispositionHeader
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.permissions import View, ModifyPortalContent

# Plone 3rd party imports
from Products.PythonField import PythonField as PythonField

# Local imports
from Products.PloneFormGen import config
from Products.PloneFormGen.config import *
from Products.PloneFormGen.content.actionAdapter import \
    FormActionAdapter, FormAdapterSchema
from Products.PloneFormGen import PloneFormGenMessageFactory as _

logger = logging.getLogger("PloneFormGen")    


# Value of new custom script body field     
default_script = """
## Python Script
##bind container=container
##bind context=context
##bind subpath=traverse_subpath
##parameters=fields, ploneformgen, request
##title=
##

# Available parameters:
#  fields  = HTTP request form fields as key value pairs
#  request = The current HTTP request. 
#            Access fields by request.form["myfieldname"]
#  ploneformgen = PloneFormGen object
# 
# Return value is not processed -- unless you
# return a dictionary with contents. That's regarded
# as an error and will stop processing of actions
# and return the user to the form. Error dictionaries
# should be of the form {'field_id':'Error message'}


assert False, "Please complete your script"

"""

class FormCustomScriptAdapter(FormActionAdapter):
    """ Executes a Python script for form data
    """

    # Python script receives parameters 
    #     resultData  - cleaned up input
    #     form        - the PFG object
    #     REQUEST
    
    # External Python script (as in Plone skins)
    SCRIPT_TYPE_SKINS_SCRIPT="skins_script"
    
    # Script defined in ScriptData field
    SCRIPT_TYPE_INTERNAL_SCRIPT="internal_script"

    schema = FormAdapterSchema.copy() + Schema((
        StringField('ProxyRole',
            searchable=0,
            required=1,
            default="none",
            read_permission=ModifyPortalContent,
            write_permission=EDIT_PYTHON_PERMISSION,
            vocabulary="getProxyRoleChoices",
            widget=SelectionWidget(
                label=_(u'label_script_proxy', default=u'Proxy role'),
                description = _(u'help_script_proxy', default=u""" Role under which to run the script. """),
                ),
            ),            
     
        PythonField('ScriptBody',
            searchable=0,
            required=0,
            default=default_script,
            read_permission=ModifyPortalContent,
            write_permission=EDIT_PYTHON_PERMISSION,
            widget=TextAreaWidget(
                label=_(u'label_script_body', default=u'Script body'),
                rows=10,
                visible={'view': 'invisible','edit': 'visible'},    
                description = _(u'help_script_body', default=u""" Write your script here. """),
                ),
            ),            
    ))

    meta_type = portal_type = 'FormCustomScriptAdapter'
    archetype_name = 'Custom Script Adapter'

    content_icon   = 'scriptaction.gif'

    #immediate_view = 'fg_savedata_view'
    #default_view   = 'fg_savedata_view'

    security = ClassSecurityInfo()
    
    def __init__(self, oid, **kwargs):
        """ initialize class """

        FormActionAdapter.__init__(self, oid, **kwargs)
        
        # for the convenience of scripters operating
        # in a restricted python environment,
        # let's store a reference to FORM_ERROR_MARKER
        # on the object, so it'll be available
        # as an attribute of context.
        self.FORM_ERROR_MARKER = config.FORM_ERROR_MARKER
    
    def updateScript(self, body, role):
        """ Regenerate Python script object 
        
        Sync set of script source code, proxy role and 
        creation of Python Script object.
        
        """         
        bodyField = self.schema["ScriptBody"]    
        proxyField = self.schema["ProxyRole"]    
        script = PythonScript(self.title_or_id())
        script = script.__of__(self)
        
        # Force proxy role     
        if role != "none":
            script.manage_proxy((role,))
        
        script.ZPythonScript_edit("fields, ploneformgen, request", body)            
                
        PythonField.set(bodyField, self, script)        
        StringField.set(proxyField, self, role)
            
    def setScriptBody(self, body):
        """ Make PythonScript construction to take parameters """    
        proxy = self.getProxyRole()        
        self.updateScript(body, proxy)
                
    def setProxyRole(self, role):
        sourceCode = self.getRawScriptBody()
        self.updateScript(sourceCode, role)
        
    def getProxyRoleChoices(self):
        """ Get proxy role choices"""
        
        # XXX TODO: use real role list
        return DisplayList(
           (("none", "No proxy role"),
            ("Manager", "Manager"),
            ))
                
    def onSuccess(self, fields, REQUEST=None):
        """ Executes the custom script
        
        """
                        
        # use PloneFormGen object as a context
        form = aq_parent(self)       
        
        if REQUEST != None:
            resultData = self.sanifyFields(REQUEST.form) 
        else:
            resultData = {}
                        
        return self.executeCustomScript(resultData, form, REQUEST)
        
    def checkWarningsAndErrors(self):
        """ Raise exception if there has been bad things with the script compiling """
        field = self.schema["ScriptBody"]      
                  
        script = ObjectField.get(field, self)
        
        if len(script.warnings) > 0:
            logger.warn("Python script " + self.title_or_id() + " has warning:" + str(script.warnings))
        
        if len(script.errors) > 0:
            logger.error("Python script "  + self.title_or_id() +  " has errors: " + str(script.errors))
            raise ValueError, "Python script "  + self.title_or_id() + " has errors: " + str(script.errors)
    
    def executeCustomScript(self, result, form, req):
        """ Execute in-place script  
        
        @param result Extracted fields from REQUEST.form
        @param form PloneFormGen object
        """        
        field = self.schema["ScriptBody"] 
        # Now pass through PythonField/PythonScript abstraction 
        # to access bad things (tm)
        # otherwise there are silent failures
        script = ObjectField.get(field, self)
                
        logger.debug("Executing Custom Script Adapter " + self.title_or_id() + " fields:" + str(result))
        
        self.checkWarningsAndErrors()        
                    
        response = script(result, form, req)    
        return response
    
    def sanifyFields(self, form):
        """ Makes request.form fields accessible in a script 
        
        Avoid Unauthorized exceptions since REQUEST.form is inaccesible
        """
        result = {}
        for field in form:
            result[field] = form[field]
        return result
        
registerATCT(FormCustomScriptAdapter, PROJECTNAME)
