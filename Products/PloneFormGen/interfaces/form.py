from zope.interface import Interface

class IPloneFormGenForm(Interface):
    """fgForm marker interface
    """
    
    def fgFields(request=None):
        """ generate fields on the fly; also primes request with defaults if request is passed """
    
    def fgvalidate(REQUEST=None, errors=None, data=None, metadata=None):
        """Validates the field data from the request.
        """

