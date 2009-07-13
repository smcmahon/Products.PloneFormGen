from Acquisition import aq_inner, aq_chain
from zope import component, interface

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

class PFGFormBuildView(BrowserView):
    """A custom edit form for pfg form that support ajaxtified form build
    """
    template = ViewPageTemplateFile('formbuild_view.pt')

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.fields = self.context._getFieldObjects()

    def __call__(self):
        return self.template()

