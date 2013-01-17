from zope.interface import implements
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation


class ExRangeValidator:
    """ Validates whether or not a numeric value is within a range.
        minval and maxval *inclusive* may come from initialization,
        from the kwargs in a call or from field attributes.
    """

    implements(IValidator)

    name = 'ExRangeValidator'

    def __init__(self, name, minval=0.0, maxval=0.0, title='', description=''):
        self.name = name
        self.minval = minval
        self.maxval = maxval
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):

        field    = kwargs.get('field', None)

        # get maxval
        if kwargs.has_key('maxval'):
            maxval = kwargs.get('maxval')
        elif hasattr(field, 'maxval'):
            maxval = float(field.maxval)
        else:
            # set to given default value (default defaults to 0)
            maxval = self.maxval

        # get minval
        if kwargs.has_key('minval'):
            minval = kwargs.get('minval')
        elif hasattr(field, 'minval'):
            minval = float(field.minval)
        else:
            # set to given default value (default defaults to 0)
            minval = self.minval

        if (minval > maxval):
            return ("Validation failed(%(name)s): minval (%(min)s) > maxval (%(max)s)" %
                { 'name' : self.name, 'min' : minval, 'max' : maxval,})

        try:
            nval = float(value)
        except ValueError:
            return ("Validation failed(%(name)s): could not convert '%(value)s' to number" %
                    { 'name' : self.name, 'value': value})

        if minval <= nval <= maxval:
            return 1

        if minval > nval:
            return ("Validation failed(%(name)s): '%(value)s' is too small. Must be at least %(min)s." %
                    { 'name' : self.name, 'value': value, 'min' : minval,})
        else:
            return ("Validation failed(%(name)s): '%(value)s' is too large. Must be no greater than %(max)s." %
                    { 'name' : self.name, 'value': value, 'max' : maxval,})

validation.register(ExRangeValidator('inExNumericRange'))
