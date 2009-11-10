from zope.interface import implements
from Products.Five import BrowserView

from Products.PloneFormGen import interfaces


class ChooseUserView(BrowserView):
    """
    View for the choose user page.
    """

    def update(self):
        pass

    def __call__(self):
        self.update()
        return super(ChooseUserView, self).__call__()
