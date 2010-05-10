from zope.interface import implements, Interface
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation


class IsCheckedValidator:
    """ Validates a Boolean field, which should have a "1" (checked)
        or "0" unchecked, to be checked.
    """

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        #BBB
        __implements__ = (IValidator, )

    name = 'IsCheckedValidator'

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):

        if (isinstancee(value, bool) and value or \
           (isinstance(value, basestring) and (value == '1'):
            return True

        return ("Validation failed(%s): must be checked." % self.name)

validation.register(IsCheckedValidator('isChecked'))


class IsUncheckedValidator:
    """ Validates a Boolean field, which should have a "1" (checked)
        or "0" unchecked, to be unchecked.
    """

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        #BBB
        __implements__ = (IValidator, )

    name = 'IsUncheckedValidator'

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):

        if (isinstance(value, bool) and not value or \
           (isinstance(value, basestring) and (value == '0'):
            return True

        return ("Validation failed(%s): must be unchecked." % self.name)

validation.register(IsUncheckedValidator('isUnchecked'))
