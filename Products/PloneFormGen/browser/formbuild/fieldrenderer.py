import sys, traceback

from zope import component
from Acquisition import aq_inner, aq_parent, aq_base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Field import Field as BaseField

from Products.PloneFormGen.interfaces import IPloneFormGenForm

class FieldRenderer(BrowserView):
    """Use to render the view,
       so that we could extend the fossil view marco
    """
    template = ViewPageTemplateFile('fieldrenderer.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        #caculate the form object, TODO: should be a field method
        self.form = aq_parent(aq_inner(self.context))
        while self.form and not IPloneFormGenForm.providedBy(self.form):
            self.form = aq_parent(self.form)
        print self.form.absolute_url()
        #View mode, default = edit
        self.mode = request.form.get('mode', 'edit')
        #Field's value, just have meaning when we're in view mode
        self.value = request.form.get('value', '')
        self.fieldname = context.getId()
        self.isATField = isinstance(aq_base(self.context).fgField,BaseField) 
        #TODO: How should we pass errors for the view when render :((
        self.errors = request.form.get('errors', {})
    
    def __call__(self):
        #TODO: Better exception handle needed ? atm just raise all of them out
        if self.form is None:
            raise("Unable to locate form object from the request.")
        if self.mode == 'view' and self.data is None:
            raise("In order to render the field in view mode, \
                   you need to call the view in an IFormData context.")
        return self.template()
        try: 
            return self.template()
        except: 
            return "<div>Error when rendering field value</div>" 

