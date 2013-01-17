from zope.interface import Interface, Attribute


class IPloneFormGenField(Interface):
    """fgField interface
    """

    # fgField -- an archetypes field; must exist as an object (not class) attribute

    meta_type = Attribute("archetypes meta type")
    """
    Must match GS type declaration.
    """

    def fgPrimeDefaults(request, useTALES=True):
        """ primes request with default """

    def fgFields(request=None):
        """ generate fields on the fly; also primes request with defaults """

    def fgvalidate(REQUEST=None, errors=None, data=None, metadata=None):
        """Validates the field data from the request.
        """

    def isLabel():
        """Returns True if this field is a label and should only be
           shown in the edit form.
        """

    def isFileField():
        """Returns True if the embedded field acts like a file field
        """

    def thanksValue(REQUEST):
        """ return from REQUEST, this field's value, rendered for display
            on a thanks page.
        """

    def htmlValue(REQUEST):
        """ return from REQUEST, this field's value, rendered as XHTML.
        """

    def getFieldFormName():
        """Returns field name as used in form and request.form.
           To be overridden when form field name varies from the field name,
           as, for example, with file field."""
