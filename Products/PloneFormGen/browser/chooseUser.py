from zope.interface import implements
from Products.Five import BrowserView

from Products.PloneFormGen import interfaces


class ChooseUserView(BrowserView):
    """
    View for the choose user page.
    """

    def update(self):
        self.users = []
        self.no_users = False

        # Work out which form was submitted and try and look up the user
        if self.request['REQUEST_METHOD'] == 'POST':
            if self.request.form.get('user-search'):
                query = self.request.form.get('user-search').lower() 
                portal = self.context.portal_url.getPortalObject()
                pmt = portal.portal_membership
                if query:
                    if getattr(portal, 'membrane_tool', None):
                        # membrane
                        memberbrains = portal.membrane_tool.searchResults(
                            SearchableText=query,
                            )
                        for b in memberbrains:
                            m = pmt.getMemberById(b['getUserId'])
                            if m:
                                self.users.append(m)
                    else:
                        # SLOW
                        # in our site, portal_membership.searchMembers doesn't
                        # help us - someone else might be able to figure this
                        # out
                        members = pmt.listMembers()
                        for m in members:
                            fn = m.getProperty('fullname')
                            un = m.getProperty('userName')
                            if fn.lower().find(query) > -1 \
                                    or un.lower().find(query) > -1:
                                self.users.append(m)
                    if not self.users:
                        self.no_users = True
            elif self.request.form.get('user-select'):
                override_key = self.request.form.get('user-select', '')
                url = self.context.absolute_url() 
                self.request.response.redirect(url + '?override_key=' + override_key)

    def __call__(self):
        self.update()
        return super(ChooseUserView, self).__call__()
