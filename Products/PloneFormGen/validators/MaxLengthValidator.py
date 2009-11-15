from zope.interface import implements, Interface
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation

from Products.CMFPlone.utils import safe_hasattr

class MaxLengthValidator:
    """ Validates whether or not a value's length is at or under
        maxlength. maxlength may come from initialization,
        from the kwargs in a call or from widget attributes.
    """

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        #BBB
        __implements__ = (IValidator, )

    name = 'MaxLengthValidator'

    def __init__(self, name, maxlength=255, title='', description=''):
        self.name = name
        self.maxlength = maxlength
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):

        #import pdb; pdb.set_trace()
            
        field = kwargs.get('field', None)
        widget = getattr(field, 'widget', None)

        # get maxlength
        if kwargs.has_key('maxlength'):
            maxlength = kwargs.get('maxlength')
        elif safe_hasattr(widget, 'maxlength'):
            maxlength = int(widget.maxlength or 0)
        else:
            # set to given default value (default defaults to 0)
            maxlength = self.maxlength

        if maxlength == 0:
            return 1

        nval = len(value)
                    
        if nval <= maxlength:
            return 1
        else:
            return ("Validation failed(%(name)s): '%(value)s' is too long. Must be no longer than %(max)s characters." %
                    { 'name' : self.name, 'value': getattr(widget, 'label', 'Entry'), 'max' : maxlength,})

validation.register(MaxLengthValidator('isNotTooLong'))
