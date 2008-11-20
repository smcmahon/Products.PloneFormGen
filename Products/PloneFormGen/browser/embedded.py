from Acquisition import aq_inner
from Products.Five import BrowserView

DEFAULT_SUBMISSION_MARKER = 'form.submitted'

class EmbeddedPFGView(BrowserView):
    """ Browser view that can update and render a PFG form in some other context
    """
    
    # Prefix to ensure that we don't try to process other forms that might
    # be on the same page
    prefix = u''
    
    def __call__(self):
        
        if self.prefix:
            form_marker = self.prefix + '.' + DEFAULT_SUBMISSION_MARKER
        else:
            form_marker = DEFAULT_SUBMISSION_MARKER

        # CMFFormController form processing is based on the presence of a 'form.submitted'
        # key in the request.  We need to translate our prefixed version.
        fiddled_submission_marker = None
        if form_marker in self.request.form:
            self.request.form['form.submitted'] = True
        elif self.prefix and DEFAULT_SUBMISSION_MARKER in self.request.form:
            # not our form; temporarily remove the form.submitted key to avoid a false positive
            fiddled_submission_marker = self.request.form['form.submitted']
            del self.request.form['form.submitted']
        
        # And we need to pass the form marker in the request so it can be inserted
        # into the form (we can't just use it as an argument to the controller template,
        # b/c then it won't survive validation)
        self.request.form['pfg_form_marker'] = form_marker
        
        # Delegate to CMFFormController page template so we can share logic with the standalone form
        context = aq_inner(self.context)
        res = context.fg_embedded_view()
        
        # Clean up
        if fiddled_submission_marker is not None:
            self.request.form['form.submitted'] = fiddled_submission_marker
        del self.request.form['pfg_form_marker']

        return res
