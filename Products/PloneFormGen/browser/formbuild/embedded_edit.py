from Acquisition import aq_base, aq_inner, aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.PloneFormGen.interfaces import IPloneFormGenForm

class EmbeddedEdit(BrowserView):
    """Quick edit form of an object
    """
    template = ViewPageTemplateFile('embedded_edit.pt')

    def __init__(self, context, request, view):
        super(BrowserView, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        #caculate the form object, TODO: should be a field object method
        self.fgform = view.fgform
        self.fieldId = context.getId()
        self.rel_path = view.rel_path
        self.errors = view.errors

    def update(self):
        pass

    def render(self):
        return self.template()
