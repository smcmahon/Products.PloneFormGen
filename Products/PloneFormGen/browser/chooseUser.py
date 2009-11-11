from zope.interface import implements
from Products.Five import BrowserView

from Products.PloneFormGen import interfaces


class ChooseUserView(BrowserView):
    """
    View for the choose user page.
    """

    def update(self):
        self.users = []
        self.no_users = ''
        self.raw_users = []
        
        # Work out which form was submitted and try and look up the user
        if self.request['REQUEST_METHOD'] == 'POST':
            if self.request.form.get('user-search'):
                query = self.request.form.get('user-search')                
                self.raw_users = self.context.portal_membership.searchMembers('fullname', query)
                # if we didn't get users, maybe we need to captialise the string
                if not self.raw_users:
                    self.raw_users = self.context.portal_membership.searchMembers('fullname', query.title())
                if not self.raw_users:
                    self.no_users = 'No users found'
            elif self.request.form.get('user-select'):
                override_key = self.request.form.get('user-select', '')
                url = self.context.absolute_url() 
                self.request.response.redirect(url + '?override_key=' + override_key)
                
        # if there were some users looked up, get their full names
        if self.raw_users:
            for user in self.raw_users:
                user_ob = self.context.portal_membership.getMemberById(user['username'])
                user_fullname = user_ob.getProperty('fullname')
                user['fullname'] = user_fullname
                self.users.append(user)

    def __call__(self):
        self.update()
        return super(ChooseUserView, self).__call__()
