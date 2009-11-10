from zope.interface import implements
from Products.Five import BrowserView

from Products.PloneFormGen import interfaces


class ChooseUserView(BrowserView):
    """
    View for the choose user page.
    """

    def update(self):
        self.all_users = self.context.portal_membership.listMembers()

        # If the user form has been submitted, send the user back to the main form
        if self.request['REQUEST_METHOD'] == 'POST':
            override_key = self.request.form.get('user-select', '')
            url = self.context.absolute_url() 
            self.request.response.redirect(url + '?override_key=' + override_key)

    def __call__(self):
        self.update()
        return super(ChooseUserView, self).__call__()
