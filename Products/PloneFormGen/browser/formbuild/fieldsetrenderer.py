import sys, traceback

from zope import component, interface
from Acquisition import aq_inner, aq_parent, aq_base

from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Field import Field as BaseField

from Products.PloneFormGen.interfaces import IPloneFormGenForm, \
                                    IPloneFormGenField, IPloneFormGenFieldset
from Products.PloneFormGen.browser.formbuild.interfaces import IPFGFieldRenderer

class FieldsetRenderer(BrowserView):
    """Render a fieldset base on the request.
    """
    template = ViewPageTemplateFile('fieldsetrenderer.pt')
    interface.implements(IPFGFieldRenderer)
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.fgform = aq_parent(aq_inner(self.context))
        while self.fgform and not IPloneFormGenForm.providedBy(self.fgform):
            self.fgform = aq_parent(aq_inner(self.fgform))
        formpath = ":".join(self.fgform.getPhysicalPath())
        #Relative path from the form object
        self.rel_path = ":".join(context.getPhysicalPath())[len(formpath)+1:]
        #Field's view mode, default = edit
        self.mode = request.form.get('mode', 'edit')
        #Field's render mode, default = edit (embed field's edit view)
        if self.mode == 'view':
            #If mode = view: We are not even in form view, but in form's data view.
            #rendermode are meaningless
            self.rendermode = ''
        else:
            self.rendermode = request.form.get('rendermode', 'edit')
        self.fieldname = context.getId()
        #TODO: How should we pass errors for the view when render :((
        self.errors = {} #request.form.get('errors', {})

    @property
    def fgfields(self):
        filters = {"object_provides": {"query":[IPloneFormGenField.__identifier__, IPloneFormGenFieldset.__identifier__], "operator": "or"}}
        return [b.getObject() for b in self.context.getFolderContents(filters)]

    def value(self):
        """Return field's value, just have meaning when we're in view mode
        """
        #TODO: Make this work with file field
        if self.mode != 'view':
            return None
        return self.request.form.get('value', '')
    
    def __call__(self):
        #TODO: Better exception handle needed ? atm just raise all of them out
        if self.fgform is None:
            raise("Unable to locate form object from the request.")
        if self.mode == 'view' and self.value is None:
            raise("In order to render the field in view mode, \
                   you need to provide the field's value.")
        return self.template()

    @property
    @memoize
    def atfields(self):
        result = []
        schematas = self.context.Schemata()
        interested_fieldsets = ['default']
        for fieldset in interested_fieldsets:
            result.extend(schematas[fieldset].editableFields(self.context, visible_only=True))
        return result

    @property
    @memoize
    def fgfield_renderers(self):
        return [field.restrictedTraverse('fieldrenderer') 
                for field in self.fgfields]

    def helperjs(self):
        """Return list of helper js-es those are needed to render the field
        """
        result = set(self.context.getUniqueWidgetAttr(self.atfields, 'helper_js'))
        for fieldrenderer in self.fgfield_renderers:
            result.update(fieldrenderer.helperjs())
        return result

    def helpercss(self):
        """Return list of helper css-es those are needed to render the field
        """
        result = set(self.context.getUniqueWidgetAttr(self.atfields, 'helper_css'))
        for fieldrenderer in self.fgfield_renderers:
            result.update(fieldrenderer.helpercss())
        return result

