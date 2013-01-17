from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

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
            if 'form_submit' in self.request.form.keys():
                return 'error'
            return 'form'
        elif IPloneFormGenThanksPage.providedBy(self.context):
            return 'thank-you'
        return None
