from zope.interface import implements, Interface
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation

class LinkSpamValidator:
    """ Validates whether or not a string has anything that seems link-like. For
    these purposes, we're considering the following fragments to be linky:
        "<a "
        "www"
        "http"
        ".com"
        (See Products.PloneFormGen.config's stringValidators for an unfortunate
        repeat of this logic.)
    """

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        #BBB
        __implements__ = (IValidator, )

    name = 'LinkSpamValidator'

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):
        # validation is optional and configured on the field
        obj = kwargs.get('field')
        if not obj:
            return 1
        if hasattr(obj,'validate_no_link_spam') and obj.validate_no_link_spam:
            bad_signs = ("<a ",
                         "www.",
                         "http:",
                         ".com",
                         )
            value = value.lower()
            for s in bad_signs:
                if s in value:
                    return ("Validation failed(%(name)s): links are not allowed." %
                            { 'name' : self.name, })
        return 1

validation.register(LinkSpamValidator('isNotLinkSpam'))
