from Products.Five import BrowserView

class FormGenView(BrowserView):
    """BrowserView"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def title(self):
        return self.context.Title()

    def embedded_form(self):
        return self.context.restrictedTraverse('fg_embedded_view_p3')()

    def portletid(self):
        return self.context.getId()
