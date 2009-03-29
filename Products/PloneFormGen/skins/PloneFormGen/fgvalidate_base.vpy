## Controller Validator "fgvalidate_base"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=
##
FORM_ERROR_MARKER = '_pfg_form_error'

try:
    from AccessControl import Unauthorized
except:
    # we can't get at Unauthorized without raising Unauthorized;
    # so a bare except is our best hope.
    Unauthorized = Exception

try:
    from Products.Archetypes import PloneMessageFactory as _
    from Products.Archetypes.utils import addStatusMessage
    P3StyleErrors = True
except (ImportError, Unauthorized):
    P3StyleErrors = False

request = context.REQUEST

errors = state.getErrors()
errors = context.fgvalidate(REQUEST=request, errors=errors, data=1, metadata=0)

if errors:
    if P3StyleErrors:
        if FORM_ERROR_MARKER in errors:
            message = errors.pop(FORM_ERROR_MARKER)
        else:
            message = _(u'Please correct the indicated errors.')
        addStatusMessage(request, message, type='error')
        return state.set(status='failure', errors=errors)
    else:
        if FORM_ERROR_MARKER in errors:
            message = errors.pop(FORM_ERROR_MARKER)
        else:
            message = 'Please correct the indicated errors.'
        return state.set(status='failure', errors=errors, portal_status_message=message)
else:
    nextAction = context.fgGetSuccessAction()
    state.setNextAction( nextAction )

    if nextAction.find('fg_result_view') > 0:
        return state.set(portal_status_message='Form validated.')

    return state
