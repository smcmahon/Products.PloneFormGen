from zope.interface import implements, Interface
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation

from zope.component import getMultiAdapter
from Acquisition import aq_inner

class CaptchaValidator:
    """ Archetypes field validator for use with collective.captcha or collective.recaptcha
    """

    if issubclass(IValidator, Interface):
        implements(IValidator)
    else:
        #BBB
        __implements__ = (IValidator, )

    name = 'CaptchaValidator'

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):
        
        context = kwargs.get('instance')
        request = kwargs.get('REQUEST')
        captcha = getMultiAdapter((context, request), name='captcha')
        if not captcha.verify(value):
            return ("Verification failed: Please type the characters you see below.")
        return 1

validation.register(CaptchaValidator('isCorrectCaptcha'))