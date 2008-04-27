from Products.validation import validation, interfaces

class IsCheckedValidator:
    """ Validates a Boolean field, which should have a "1" (checked)
        or "0" unchecked, to be checked.
    """

    __implements__ = (interfaces.ivalidator,)

    name = 'IsCheckedValidator'

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):

        # import pdb; pdb.set_trace()

        if value == '1':
            return 1

        return ("Validation failed(%s): must be checked." % self.name)

validation.register(IsCheckedValidator('isChecked'))


class IsUncheckedValidator:
    """ Validates a Boolean field, which should have a "1" (checked)
        or "0" unchecked, to be unchecked.
    """

    __implements__ = (interfaces.ivalidator,)

    name = 'IsUncheckedValidator'

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):

        # import pdb; pdb.set_trace()

        if value == '0':
            return 1

        return ("Validation failed(%s): must be unchecked." % self.name)

validation.register(IsUncheckedValidator('isUnchecked'))
