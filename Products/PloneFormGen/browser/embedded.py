from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.PloneFormGen import HAS_PLONE30

DEFAULT_SUBMISSION_MARKER = 'form.submitted'

"""
Cases that won't work / need testing or thinking through
- success override that uses a traverse_to action (actually theoretically valid,
  as long as the thing being traversed to doesn't pull in main_template)
- do we need to buffer anything else besides the submission marker and
  controller state?
"""

class EmbeddedPFGView(BrowserView):
    """ Browser view that can update and render a PFG form in some other context
    """
    
    # Prefix to ensure that we don't try to process other forms that might
    # be on the same page
    prefix = u''
    
    # optional form action override
    action = None
    
    def setPrefix(self, prefix):
        self.prefix = prefix
        
    def setAction(self, action):
        self.action = action
    
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
        
        # temporarily clear out the controller_state from the request in case we're embedded in
        # another controller page template
        fiddled_controller_state = self.request.get('controller_state', None)
        self.request.set('controller_state', None)
        
        # pass the form action override
        # (we do this in the request instead of passing it in when calling the .cpt, because
        # the .cpt might end up getting called again after validation or something)
        if self.action is not None:
            self.request.set('pfg_form_action', self.action)
        else:
            self.request.set('pfg_form_action', self.request['URL'])
        
        # Delegate to CMFFormController page template so we can share logic with the standalone form
        try:
            context = aq_inner(self.context)
            if HAS_PLONE30:
                return context.fg_embedded_view_p3()
            else:
                return context.fg_embedded_view()
        finally:
            # Clean up
            if fiddled_submission_marker is not None:
                self.request.form['form.submitted'] = fiddled_submission_marker
            if fiddled_controller_state is not None:
                self.request.set('controller_state', fiddled_controller_state)
            del self.request.form['pfg_form_marker']
            del self.request.other['pfg_form_action']
