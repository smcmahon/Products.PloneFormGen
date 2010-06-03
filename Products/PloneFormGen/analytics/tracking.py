from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from collective.googleanalytics.tracking import AnalyticsBaseTrackingPlugin
from Products.PloneFormGen.interfaces import IPloneFormGenForm, \
    IPloneFormGenThanksPage

class PFGAnalyticsPlugin(AnalyticsBaseTrackingPlugin):
    """
    A tracking plugin to track form views, submissions and errors.
    """

    __call__ = ViewPageTemplateFile('tracking.pt')
    
    def form_status(self):
        """
        Returns the status of the form, which can be None (not a form),
        'form' (viewing the form), 'thank-you' (form succesfully submitted),
        or 'error' (form has validation errors).
        """
        
        if IPloneFormGenForm.providedBy(self.context):
            request_method = self.request.environ.get('REQUEST_METHOD', 'GET')
            if request_method == 'GET':
                return 'form'
            return 'error'
        elif IPloneFormGenThanksPage.providedBy(self.context):
            return 'thank-you'
        return None
