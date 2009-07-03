from Acquisition import aq_base, aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.PloneFormGen.interfaces import IPloneFormGenForm

class EditEmbedded(BrowserView):
    """Use to render the view,
       so that we could extend the fossil view marco
    """
    template = ViewPageTemplateFile('edit_embedded.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        #caculate the form object, TODO: should be a field method
        self.form = aq_parent(aq_inner(self.context))
        while self.form and not IPloneFormGenForm.providedBy(self.form):
            self.form = aq_parent(self.form)
        #TODO: How should we pass errors for the view when render :((
        self.errors = request.form.get('errors', {})

    def __call__(self):
        return self.template()

