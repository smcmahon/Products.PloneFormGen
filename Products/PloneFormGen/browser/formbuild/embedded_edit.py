from Acquisition import aq_base, aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.PloneFormGen.interfaces import IPloneFormGenForm

class EmbeddedEdit(BrowserView):
    """Use to render the view,
       so that we could extend the fossil view marco
    """
    template = ViewPageTemplateFile('embedded_edit.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        #caculate the form object, TODO: should be a field method
        self.form = aq_parent(aq_inner(self.context))
        while self.form and not IPloneFormGenForm.providedBy(self.form):
            self.form = aq_parent(self.form)
        self.field = context
        self.fieldId = context.getId()
        self.errors = self.request.form.get('errors',{})

    def __call__(self):
        return self.template()
