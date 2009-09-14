from zope.interface import implements
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.content.browser.folderfactories import _allowedTypes

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import IConstrainTypes

from Products.PloneFormGen.interfaces import IPloneFormGenForm
from Products.PloneFormGen.browser.formbuild.interfaces import IPFGFormBuildView

class IAddnewPortlet(IPortletDataProvider):
    pass

class Assignment(base.Assignment):
    implements(IAddnewPortlet)

    @property
    def title(self):
        """
        """
        return "Add new objects"


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('addnew.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.membership = getToolByName(self.context, 'portal_membership')
        self.portal_state = getMultiAdapter((context, request), \
                                                    name=u'plone_portal_state')
        self.factories_view = getMultiAdapter((self.context, self.request), \
                                                    name='folder_factories')
        self.addContext = self.factories_view.add_context()

    def show(self):
        #+ If you don't have permission, you'll also unable to see this
        #+ When we are not in a form object, you shouldn't see this too
        return IPloneFormGenForm.providedBy(self.context) and \
               IPFGFormBuildView.providedBy(self.view) and \
               self.membership.checkPermission('Modify portal content', \
                                                                self.context) 

    @property
    def available(self):
        return self.show() 

    def show_more(self):
        """Did we have more addable types ?
        """
        #TODO: do we really need this func ?
        allowedTypes = _allowedTypes(self.request, self.addContext)
        constraints = IConstrainTypes(self.addContext, None)
        if constraints is not None:
            include = constraints.getImmediatelyAddableTypes()
            if len(include) < len(allowedTypes):
                return True
        return False

    def addable_types(self):
        """
        """
        include = None
        constraints = IConstrainTypes(self.addContext, None)
        if constraints is not None:
            include = constraints.getImmediatelyAddableTypes()
        return self.factories_view.addable_types(include=include)

