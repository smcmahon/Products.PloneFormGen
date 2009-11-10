from zope.interface import implements
from Products.Five import BrowserView

from Products.PloneFormGen import interfaces


class ChooseUserView(BrowserView):
    """
    View for the choose user page.
    """

    def update(self):
        self.all_users = self.context.portal_membership.listMembers()

    def __call__(self):
        self.update()
        return super(ChooseUserView, self).__call__()
