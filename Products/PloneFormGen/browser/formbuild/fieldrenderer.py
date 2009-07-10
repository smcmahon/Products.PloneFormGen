import sys, traceback

from zope import component
from Acquisition import aq_inner, aq_parent, aq_base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Field import Field as BaseField

from Products.PloneFormGen.interfaces import IPloneFormGenForm

class FieldRenderer(BrowserView):
    """Render a field base on the request.
    """
    template = ViewPageTemplateFile('fieldrenderer.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.form = aq_parent(aq_inner(self.context))
        while self.form and not IPloneFormGenForm.providedBy(self.form):
            self.form = aq_parent(self.form)
        #Field's view mode, default = edit
        self.mode = request.form.get('mode', 'edit')
        #Field's render mode, default = edit (embed field's edit view)
        if self.mode == 'view':
            #If mode = view: We are not even in form view, but in form's data view.
            #rendermode are meaningless
            self.rendermode = ''
        else:
            self.rendermode = request.form.get('rendermode', 'edit')
        if self.rendermode == 'edit':
            self.editview = component.getMultiAdapter((context, request), name='embedded_edit')
        self.fieldname = context.getId()
        self.isATField = isinstance(aq_base(self.context).fgField,BaseField) 
        #TODO: How should we pass errors for the view when render :((
        self.errors = request.form.get('errors', {})

    def value(self):
        """Return field's value, just have meaning when we're in view mode
        """
        #TODO: Make this work with file field
        if self.mode != 'view':
            return None
        return self.request.form.get('value', '')
    
    def __call__(self):
        #TODO: Better exception handle needed ? atm just raise all of them out
        if self.form is None:
            raise("Unable to locate form object from the request.")
        if self.mode == 'view' and self.value is None:
            raise("In order to render the field in view mode, \
                   you need to provide the field's value.")
        return self.template()


